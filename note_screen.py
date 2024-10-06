import sys

import pygame.draw

from controller import FallController
from note import Note, NoteMap

PINK = (255, 192, 203)
GREEN = (0, 255, 0)
BLUE = (173, 216, 230)
GREEN_50 = (0, 255, 0, 128)


class NoteMapScreen:

    def __init__(self, noteMapPath: str):
        self.controller: FallController | None = None
        self.startAt: int = -1
        self.noteMapPath: str = noteMapPath
        self.noteColor = (255, 255, 255)
        self.trackColor = (0, 0, 255)
        self.judgeColor = (0, 255, 255)
        self.backgroundColor = (0, 0, 0)
        self.size: tuple[int, int] = (0, 0)
        self.paddingHorizontal = 10
        self.screen = None

    def init(self):
        print("生成谱面中...")
        self.__loadMap()
        print(f"生成完毕! 音符数量: {len(self.controller.notes)}")
        self.size = (self.controller.trackWidth * self.controller.trackNums + 20,
                     self.controller.validHeight + 50)
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Map Viewer")

    def __loadMap(self):
        self.controller = FallController(NoteMap.load(self.noteMapPath))

    def update(self):
        progress = pygame.mixer.music.get_pos()

        self.drawTracks()

        self.controller.update(progress)

    def drawTracks(self):
        self.screen.fill(self.backgroundColor)
        trackWidth = self.controller.trackWidth
        validHeight = self.controller.validHeight
        width, height = self.size
        for i in range(self.controller.trackNums + 1):
            x = self.paddingHorizontal + i * trackWidth
            pygame.draw.line(self.screen, self.trackColor, (x, 0), (x, validHeight))

        # 绘制判定线
        pygame.draw.line(self.screen, self.judgeColor, (self.paddingHorizontal, validHeight),
                         (width - self.paddingHorizontal, validHeight))

    def drawNotes(self, note: Note):
        noteWidth, noteHeight = self.controller.noteSize
        if note.type == Note.TAP:
            color = BLUE
            pygame.draw.rect(self.screen, color, (self.paddingHorizontal + note.x, note.y, noteWidth, noteHeight))
        elif note.type == Note.FLICK:
            color = PINK
            pygame.draw.polygon(self.screen, color, [
                (self.paddingHorizontal + note.x + noteWidth / 2, note.y),
                (self.paddingHorizontal + note.x, note.y + noteHeight),
                (self.paddingHorizontal + note.x + noteWidth, note.y + noteHeight),
            ])
        elif note.type == Note.SLIDE:
            color = GREEN
            pygame.draw.rect(self.screen, color, (self.paddingHorizontal + note.x, note.y, noteWidth, noteHeight))
            nextNote = note.next
            if nextNote is not None:
                nextY = nextNote.y + noteHeight / 2
                suf = pygame.Surface(self.size, pygame.SRCALPHA)
                pygame.draw.line(suf, GREEN_50,
                                 (self.paddingHorizontal + nextNote.x + noteWidth / 2, nextY),
                                 (self.paddingHorizontal + note.x + noteWidth / 2, note.y + noteHeight / 2),
                                 width=25
                                 )
                self.screen.blit(suf, (0, 0))
