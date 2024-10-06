import sys

import pygame

from note import Note
from note_screen import NoteMapScreen

pygame.init()

# 音频
musicPath = "data/bokuha.mp3"
# 谱面信息
mapPath = "data/bokuha.json"

noteMap = NoteMapScreen(mapPath)
noteMap.init()
noteMap.controller.fallSpeed = 10

pygame.mixer.init(channels=16)

pygame.mixer.music.load(musicPath)
perfect = pygame.mixer.Sound("data/perfect.mp3")
flick = pygame.mixer.Sound("data/flick.mp3")
slide = pygame.mixer.Sound("data/slide.mp3")
channel_perfect = pygame.mixer.Channel(0)
channel_slide = pygame.mixer.Channel(1)
channel_flick = pygame.mixer.Channel(2)
perfect.set_volume(0.3)
flick.set_volume(0.3)
slide.set_volume(0.5)

clock = pygame.time.Clock()


def onSlide():
    if not channel_slide.get_busy():
        channel_slide.play(slide)


def onDead(note: Note):
    if note.type == Note.TAP or note.type == Note.SLIDE:
        channel_perfect.play(perfect)
    elif note.type == Note.FLICK:
        channel_flick.play(flick)


noteMap.controller.onUpdateListener = noteMap.drawNotes
noteMap.controller.onDeadListener = onDead
noteMap.controller.onSlideListener = onSlide

pygame.mixer.music.play()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    noteMap.update()

    pygame.display.flip()

    clock.tick(120)
