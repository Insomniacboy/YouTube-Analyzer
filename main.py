# Description: Main file for the project

# Imports
import datetime
import requests
import json
import os
from youtube import YouTube
import re
import csv
import locale
from decimal import Decimal
from InquirerPy import inquirer
from InquirerPy import prompt
import random
from moviepy.editor import *

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

# Progress bar for analyzing channels
def print_progress_bar(nProcessed, nTotal, barLength=50):
    percent = float(nProcessed) / nTotal
    arrow = '-' * int(round(percent * barLength)-1) + '>'
    spaces = ' ' * (barLength - len(arrow))
    print('Прогресс: [%s%s] %d %%' % (arrow, spaces, percent*100), end='\r')

# Hash function for mashup
def hash(s):
    hash = 0
    for c in s:
        hash = ord(c) + (hash << 6) + (hash << 16) - hash
    return hash

# Main function
if __name__ == '__main__':
    try:
        # set locale
        locale.setlocale(locale.LC_ALL, 'en_US')

        # make choice whether analyze or create mashup using InquirerPy
        questions = [
            {"type": "list", "message": "Выберите опцию", "name": "choice", "choices": ["Анализ каналов", "Создание мэшапа"]}
        ]
        answers = prompt(questions)
        if answers["choice"] == "Анализ каналов":
            # get sample size from input
            print('Введите размер выборки: ', end='')

            while True:
                try:
                    sample_size = int(input())
                    break
                except ValueError:
                    print('Неверный ввод. Введите целое число: ', end='')

            # create nProcessed and nTotal
            nProcessed = 0
            nTotal = 0
            with open('channels.txt', 'r') as f:
                nTotal = len(f.readlines())

            # read from channels.txt and create object for each channel
            channels = []
            with open('channels.txt', 'r') as f:
                for line in f:
                    channels.append(YouTube(line.strip(), sample_size))
                    nProcessed += 1
                    print_progress_bar(nProcessed, nTotal)

            # Write to Excel file
            csv_columns = ['Channel', 'Video', 'Views', 'Likes', 'URL', 'Date']
            with open('output.csv', 'w') as f:
                writer = csv.DictWriter(f, fieldnames=csv_columns)
                writer.writeheader()
                for channel in channels:
                    for video in channel.videos:
                        try:
                            views = "{:,}".format(int(video.views))
                            likes = "{:,}".format(int(video.likes))
                        except:
                            views = video.views
                            likes = video.likes
                        writer.writerow({'Channel': channel.author, 'Video': emoji_pattern.sub(r'', video.title), 'Views': views, 'Likes': likes, 'URL': video.url, 'Date': video.date})
        else:
            # get sample size from input
            print('Введите количество последних видео для анализа (минимум 15): ', end='')

            while True:
                try:
                    sample_size = int(input())
                    if sample_size < 15:
                        raise ValueError
                    break
                except ValueError:
                    print('Неверный ввод. Введите целое число (минимум 15): ', end='')

            mashupList = []

            while True:

                print('Обработка видео...')

                # We create mashup by structure: 1 last video from my channel, 5 video with highest retention rate, 4-5 videos chosen randomly except already chosen

                myChannel = YouTube(sample_size)

                mashupList = []

                print('Создание списка для мэшапа...')

                # add last video from my channel

                mashupList.append(myChannel.videos[0])

                # take 10 videos with highest retention rate and pick 5 of them randomly

                # sort videos by retention rate

                myChannel.videos.sort(key=lambda x: x.retention_rate, reverse=True)
                
                # create list of 10 videos with highest retention rate

                top10 = myChannel.videos[:10]

                # pick 5 different videos randomly also check that it is not already chosen

                for i in range(5):
                    randomIndex = random.randint(0, 9)
                    while top10[randomIndex] in mashupList:
                        randomIndex = random.randint(0, 9)
                    mashupList.append(top10[randomIndex])
                
                # pick 4 videos randomly except already chosen

                for i in range(4):
                    randomIndex = random.randint(0, sample_size - 1)
                    while myChannel.videos[randomIndex] in mashupList:
                        randomIndex = random.randint(0, sample_size - 1)
                    mashupList.append(myChannel.videos[randomIndex])

                # sort mashup list by title

                mashupList.sort(key=lambda x: x.title)

                print('Список для мэшапа создан. Хэшируем...')

                # create hash for mashup
                mashupHash = 0
                for video in mashupList:
                    mashupHash += hash(video.title)
                mashupHash = mashupHash % 1000000

                # mashupNameList
                mashupNameList = []
                for video in mashupList:
                    mashupNameList.append(video.title)

                # write or add hash mashup to db/mashups.csv

                # check if mashups.csv exists

                isAdded = False

                if os.path.isfile('db/mashups.csv'):
                    # read mashups.csv
                    with open('db/mashups.csv', 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row['Hash'] == str(mashupHash):
                                print('Мэшап с таким хэшем уже существует')
                    # add mashup to mashups.csv
                    with open('db/mashups.csv', 'a') as f:
                        writer = csv.DictWriter(f, fieldnames=['Hash', 'Videos'])
                        writer.writerow({'Hash': mashupHash, 'Videos': mashupNameList})
                        isAdded = True
                else:
                    # create mashups.csv
                    with open('db/mashups.csv', 'w') as f:
                        writer = csv.DictWriter(f, fieldnames=['Hash', 'Videos'])
                        writer.writeheader()
                        writer.writerow({'Hash': mashupHash, 'Videos': mashupNameList})
                        isAdded = True
                
                if isAdded:
                    break

            print('Загрузка исходных видео...')
            
            # download videos from mashupList to mashup folder

            videoCnt = 0

            for video in mashupList:
                video.download()
                videoCnt += 1
                print('{}/10'.format(videoCnt), end='\r')

            print('Создание мэшапа...')

            # create mashup.mp4 from videos in mashup folder

            mashup = VideoFileClip('./data/videos/' + mashupList[0].title + '.mp4').fx(vfx.speedx, mashupList[0].speed_rate)
            for i in range(1, 10):
                video = VideoFileClip('./data/videos/' + mashupList[i].title + '.mp4').fx(vfx.speedx, mashupList[i].speed_rate)
                mashup = concatenate_videoclips([mashup, video])
            mashup.write_videofile('./data/mashups/mashup-{}.mp4'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')), codec='libx264', audio_codec='aac', bitrate='10000k')

            print('Удаление исходных видео...')

            # delete videos from mashup folder

            for video in mashupList:
                os.remove('./data/videos/' + video.title + '.mp4')
    except KeyboardInterrupt:
        print('Выполнение программы прервано')
