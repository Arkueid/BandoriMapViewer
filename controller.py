from typing import Callable

from note import Note, INT_UNINITIALIZED, NoteMap, NoteMeta


class FallController:
    """
    下落控制器
    """
    # 5000 ms, 每个音符的初始下落时间
    defaultFallTime = 5000

    def __init__(self, noteMap: NoteMap):
        self.noteMap: NoteMap = noteMap
        # 每毫秒 beat 数
        self.bpms: float = self.noteMap.bpm.bpm / 60 / 1000
        # 音符列表
        self.notes: list[Note] = self.__generateNotes(noteMap.notes)
        # 每个轨道最晚生成的 note
        self.__trackLastNotes: dict[int, Note | None] = dict()
        # 轨道宽度
        self.trackWidth: int = 100
        # 轨道高度
        self.trackHeight: int = 500
        # 轨道数
        self.trackNums: int = 7
        # 轨道内距
        self.trackPadding: int = 10
        # 音符宽高
        self.noteSize = (self.trackWidth - self.trackPadding * 2, 25)
        # 有效高度, 音符出现位置到判定线的距离
        self.validHeight: int = 400
        # 同一个轨道音符间的最小距离
        self.minDY: int = 100
        # 下落速度
        self.__fallSpeed: float = 1
        # 下落时间
        self.__fallTime: float = int(self.defaultFallTime * self.bpms / self.__fallSpeed)
        # 音符在到达判定线后可以存活的时间
        self.__validTime: float = int(100 * self.bpms / self.fallSpeed)

        self.trackIds = [i for i in range(self.trackNums)]

        # update 回调，用于绘制音符
        self.onUpdateListener: Callable[[Note], None] | None = None
        # 音符消失
        self.onDeadListener: Callable[[Note], None] | None = None
        # 滑动
        self.onSlideListener: Callable[[], None] | None = None

    @property
    def fallSpeed(self):
        return self.__fallSpeed

    @fallSpeed.setter
    def fallSpeed(self, value: float):
        self.__fallSpeed = value
        self.__fallTime = int(self.defaultFallTime * self.bpms / value)
        self.__validTime = int(100 * self.bpms / value)

    def update(self, progress: int):
        progress = progress * self.bpms

        self.__trackLastNotes.clear()
        liveHeight = self.validHeight + self.noteSize[1] / 2
        for note in self.notes:

            if not note.dead:
                note.y = round(liveHeight * (1 - (note.progress - progress) / (self.__fallTime + self.__validTime))) - \
                         self.noteSize[1]

            # 未分配过轨道则进行初始化
            if note.x == INT_UNINITIALIZED:
                note.x = note.lane * self.trackWidth + self.trackPadding

            # 未播放到
            if note.progress - self.__fallTime > progress:
                continue

            # 已播放完毕
            if note.progress + self.__validTime < progress:
                if not note.dead:
                    note.dead = True
                    if self.onDeadListener is not None:
                        self.onDeadListener(note)

                if note.type != Note.SLIDE or note.next is None or note.next.dead:
                    continue

                trueY = round(liveHeight * (1 - (note.progress - progress) / (self.__fallTime + self.__validTime))) - \
                        self.noteSize[1]
                trueX = note.lane * self.trackWidth + self.trackPadding
                dx = trueX - note.next.x
                dy = trueY - note.next.y
                note.x = trueX + dx / dy * (liveHeight - trueY)
                self.onSlideListener()

            self.__trackLastNotes[note.lane] = note

            # 执行回调，主要是绘制
            if self.onUpdateListener is not None:
                self.onUpdateListener(note)

    @staticmethod
    def __generateNotes(notes: list[NoteMeta]) -> list[Note]:
        newNotes = list()
        for i in notes:
            note = Note(i)
            if note.type == Note.SLIDE:
                while note.next is not None:
                    newNotes.append(note.next)
                    note = note.next
            else:
                newNotes.append(note)
        return newNotes
