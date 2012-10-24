import pygame
import urllib
import json

def play(filename):
	pygame.mixer.init()
	pygame.mixer.music.load(filename)
	pygame.mixer.music.play()

	while pygame.mixer.music.get_busy():
		pygame.time.Clock().tick(10)

playListURL = r'http://douban.fm/j/mine/playlist?type=n&channel=1&from=mainsite'
channelURL = r'&channel=' + str(1)
fromURL = r'&from=mainsite'

url = playListURL + channelURL + fromURL

page_source = urllib.urlopen(url)
pageData = page_source.read()
jsonData = json.loads(pageData)
songList = jsonData['song']

for song in songList:
	print(song['title'] + "  <<" + song['albumtitle'] + ">>" + " -- " + song['artist'])
	print(song['url'])

#play('test.mp3')
