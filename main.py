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

# Convert human readable time to seconds
def convert_to_seconds(time):
    minutes = time.split(':')[0]
    seconds = time.split(':')[1]
    return int(minutes) * 60 + int(seconds)

# Convert seconds to human readable time
def convert_to_time(seconds):
    minutes = int(seconds / 60)
    seconds = int(seconds % 60)
    return '{:02d}:{:02d}'.format(minutes, seconds)

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
            csv_columns = ['Channel', 'Video', 'Views', 'Date', 'Likes', 'URL']
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
                        writer.writerow({'Channel': channel.author, 'Video': emoji_pattern.sub(r'', video.title), 'Views': views, 'Date': video.date, 'Likes': likes, 'URL': video.url})
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

                # We create mashup by structure: 1 last video from my channel, 6 video with highest retention rate, 6 videos chosen randomly except already chosen

                myChannel = YouTube(sample_size)

                mashupList = []

                print('Создание списка для мэшапа...')

                questions = [
                    {"type": "list", "message": "Сделать первым видео:", "name": "choice", "choices": ["Последнее на канале", "Добавить вручную по cсылке"]},
                ]
                answers = prompt(questions)

                if answers["choice"] == "Последнее на канале":

                    myChannel.videos[0].set_speed_rate(1.00)

                    # add last video from my channel

                    mashupList.append(myChannel.videos[0])

                else: 
                    questions = [
                        {"type": "input", "message": "Введите ссылку на видео:", "name": "url"},
                    ]
                    answers = prompt(questions)

                    myChannel.appendVideo(answers["url"].split('=')[1])

                    # change speed rate for added video

                    myChannel.videos[len(myChannel.videos) - 1].set_speed_rate(1.00)

                    # add this video to mashupList

                    mashupList.append(myChannel.videos[len(myChannel.videos) - 1])

                # take 10 videos with highest retention rate and pick 5 of them randomly

                # sort videos by retention rate

                myChannel.videos.sort(key=lambda x: x.retention_rate, reverse=True)
                
                # create list of 10 videos with highest retention rate

                top10 = myChannel.videos[:10]

                # pick 6 different videos randomly also check that it is not already chosen

                for i in range(6):
                    randomIndex = random.randint(0, len(top10) - 1)
                    while top10[randomIndex] in mashupList:
                        randomIndex = random.randint(0, len(top10) - 1)
                    mashupList.append(top10[randomIndex])
                
                # pick 6 videos randomly except already chosen

                for i in range(6):
                    randomIndex = random.randint(0, len(myChannel.videos) - 1)
                    while myChannel.videos[randomIndex] in mashupList:
                        randomIndex = random.randint(0, len(myChannel.videos) - 1)
                    mashupList.append(myChannel.videos[randomIndex])

                # create copy of mashupList to hash

                mashupListCopy = mashupList.copy()

                # sort mashup list by title

                mashupListCopy.sort(key=lambda x: x.title)

                print('Список для мэшапа создан. Хэшируем...')

                # create hash for mashup
                mashupHash = 0
                for video in mashupListCopy:
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

            # create timestamps for mashup in a format like this: 00:00 - 00:30 Video Title; don't forget to count speed rate

            timestamps = []

            curr_time = '00:00'

            # create mashup.mp4 from videos in mashup folder

            mashup = VideoFileClip('./data/videos/' + mashupList[0].safe_title + '.mp4').fx(vfx.speedx, mashupList[0].speed_rate)
            timestamps.append(curr_time + ' - ' + mashupList[0].title)
            curr_time = convert_to_time(mashupList[0].duration / mashupList[0].speed_rate)
            for i in range(1, 10):
                video = VideoFileClip('./data/videos/' + mashupList[i].safe_title + '.mp4').fx(vfx.speedx, mashupList[i].speed_rate)
                mashup = concatenate_videoclips([mashup, video])
                timestamps.append(curr_time + ' - ' + mashupList[i].title)
                curr_time = convert_to_time(mashupList[i].duration / mashupList[i].speed_rate + convert_to_seconds(curr_time))

            # check if mashups folder exists
            if not os.path.isdir('./data/mashups'):
                os.mkdir('./data/mashups')
            mashup.write_videofile('./data/mashups/mashup-{}.mp4'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')), codec='libx264', audio_codec='aac', bitrate='10000k')

            print('Запись таймстампов...')

            # write timestamps to txt file

            with open('./data/mashups/mashup-{}.txt'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')), 'w') as f:
                for timestamp in timestamps:
                    f.write(timestamp + '\n')

            print('Удаление исходных видео...')

            # delete videos from mashup folder

            for video in mashupList:
                os.remove('./data/videos/' + video.safe_title + '.mp4')
    except KeyboardInterrupt:
        print('Выполнение программы прервано')
