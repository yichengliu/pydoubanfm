import pygame
import urllib2
import urllib
import json
import threading
import sys
import os
import termios
import cookielib
from cStringIO import StringIO
from pysqlite2 import dbapi2 as sqlite

class NullPlaylistError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

empty = threading.Semaphore(5)
full = threading.Semaphore(0)
queue = []
tmp_dir = '/tmp/Goban/'
home_dir = os.path.expanduser('~')

TERMIOS = termios
def getch():
	fd = sys.stdin.fileno()
	old = termios.tcgetattr(fd)
	new = termios.tcgetattr(fd)
	new[3] = new[3] & ~TERMIOS.ICANON & ~TERMIOS.ECHO
	new[6][TERMIOS.VMIN] = 1
	new[6][TERMIOS.VTIME] = 0
	termios.tcsetattr(fd, TERMIOS.TCSANOW, new)
	c = None
	try:
		c = os.read(fd, 1)
	finally:
		termios.tcsetattr(fd, TERMIOS.TCSAFLUSH, old)
	return c

# a useful function from others
def sqlite2cookie(filename,host):
    con = sqlite.connect(filename)
    con.text_factory = str
    cur = con.cursor()
    cur.execute("select host, path, isSecure, expiry, name, value from moz_cookies where host like ?"
            ,['%%%s%%' % host])
    ftstr = ["FALSE","TRUE"]
    s = StringIO()
    s.write("""\
# Netscape HTTP Cookie File
# http://www.netscape.com/newsref/std/cookie_spec.html
# This is a generated file!  Do not edit.
""")
    for item in cur.fetchall():
        s.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
            item[0], ftstr[item[0].startswith('.')], item[1],
            ftstr[item[2]], item[3], item[4], item[5]))
    s.seek(0)
    cookie_jar = cookielib.MozillaCookieJar()
    cookie_jar._really_load(s, '', True, True)
    return cookie_jar

def play(filename):
	pygame.mixer.music.load(filename)
	pygame.mixer.music.play()

	while pygame.mixer.music.get_busy():
		pygame.time.Clock().tick(10)

def report_worker(type_id):
	url = r'http://douban.fm/j/mine/playlist?type=' + type_id + '&status=p&sid=' + current_sid + '&channel=' + str(channel)
	result = urllib2.urlopen(url).read()

def play_worker():
	try:
		while True:
			full.acquire()
			song, f = queue.pop(0)

			print(song['title'] + ' <<' + song['albumtitle'] + '>> -- ' + song['artist'] + (' (Liked!)' if song['like'] == 1 else ''))

			global current_sid
			current_sid = song['sid']

			play(f)

			global skip

			if skip:
				skip = False
			else:
				threading.Thread(target=report_worker, args=('e')).start()

			current_sid = None
			empty.release()
	finally:
		pygame.mixer.music.stop()

def download_worker():
	try:
		# get cookie
		cookiejar = sqlite2cookie(home_dir + '/.mozilla/firefox/nlq33w25.default/cookies.sqlite','douban')
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
		urllib2.install_opener(opener)

		# post cookie
		url='http://douban.fm/mine'
		req=urllib2.Request(url)
		req.add_header('User-Agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')
		urllib2.urlopen(req).read()

		while True:
			playListURL = r'http://douban.fm/j/mine/playlist?type=n'
			channelURL = r'&channel=' + str(channel)
			fromURL = r'&from=mainsite'
	
			url = playListURL + channelURL + fromURL

			page_source = urllib2.urlopen(url)
			pageData = page_source.read()
			jsonData = json.loads(pageData)
			songList = jsonData['song']

			if len(songList) == 0:
				print('Can\'t get play list, you must login douban using ff before you can use favorite channel')
				raise NullPlaylistError

			for song_info in songList:
				empty.acquire()
				filename = tmp_dir + song_info['url'].split('/')[-1]

				urllib.urlretrieve(song_info['url'], filename)

				queue.append((song_info, filename))

				full.release()
	finally:
		pass

if len(sys.argv) < 2:
	print('Provide channel')
	exit()

if not os.path.exists(tmp_dir):
	os.mkdir(tmp_dir)

pygame.mixer.init()
volume = 1.0
is_mute = False
skip = False
pygame.mixer.music.set_volume(volume)
paused = False
current_sid = None

channel = int(sys.argv[1])
print('Playing channel ' + str(channel))
print('Press \'h\' for help')

player = threading.Thread(target=play_worker)
downloader = threading.Thread(target=download_worker)

player.daemon = True
downloader.daemon = True

player.start()
downloader.start()

while True:
	c = getch()

	if c == 'q':
		break

	if c == 'h':
		manual = {
			'q' : 'exit',
			'n' : 'skip this song',
			'm' : 'mute/unmute',
			'j/k' : 'increase/decrease volume',
			'p' : 'pause/unpause',
			'r' : 'Add to favorate'
		}

		for key in manual:
			print(key + ' ' + manual[key])

	if c == 'n':
		skip = True
		pygame.mixer.music.stop()

	if c == 'm':
		if is_mute:
			pygame.mixer.music.set_volume(volume)
			is_mute = False
		else:
			pygame.mixer.music.set_volume(0)
			is_mute = True

	if c == 'j':
		volume = 0 if volume < 0.1 else (volume - 0.1)
		pygame.mixer.music.set_volume(volume)

	if c == 'k':
		volume = 1 if volume > 0.9 else (volume + 0.1)
		pygame.mixer.music.set_volume(volume)

	if c == 'p':
		if paused:
			pygame.mixer.music.unpause()
			paused = False
		else:
			pygame.mixer.music.pause()
			paused = True

	if c == 'r':
		if current_sid != None:
			report = threading.Thread(target=report_worker, args=('r'))
			report.start()
			print('Like this one!')

#clean tmp files
for dirname, dirnames, filenames in os.walk(tmp_dir):
	for filename in filenames:
		os.remove(os.path.join(dirname, filename))

print('Bye')
