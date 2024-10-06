import json

INT_UNINITIALIZED = -1
STR_UNINITIALIZED = ""
FLOAT_UNINITIALIZED = -1


class BPM:

    def __init__(self, ntype: str, bpm: float, beat: float):
        self.type: str = ntype
        self.bpm: float = bpm
        self.beat: float = beat

    @property
    def json(self) -> dict:
        return {
            "type": self.type,
            "beat": self.beat,
            "bpm": self.bpm
        }

    @staticmethod
    def from_json(data: dict):
        return BPM(
            data['type'],
            data['bpm'],
            data['beat']
        )


class NoteConnection:

    def __init__(self, beat: float, lane: int):
        self.beat: float = beat
        self.lane: int = lane

    @property
    def json(self) -> dict[str, int | float]:
        return {
            "beat": self.beat,
            "lane": self.lane
        }


TYPE_SINGLE = "Single"
TYPE_SLIDE = "Slide"
TYPE_BPM = "BPM"


class NoteMeta:

    def __init__(self, ntype: str, lane: int, beat: float, flick: bool = False,
                 connections: list[NoteConnection] = None):
        self.type: str = ntype
        self.lane: int = lane
        self.beat: float = beat
        self.flick: bool = flick
        self.connections: list[NoteConnection] | None = connections

    @property
    def json(self) -> dict[str, int | float | list[dict[str, int | float]]]:
        d = {
            "type": self.type,
            "lane": self.lane,
            "beat": self.beat,
        }
        if self.flick:
            d["flick"] = True
        if self.connections is not None:
            d["connections"] = [i.json for i in self.connections]
        return d

    @staticmethod
    def from_json(data: dict):
        note_type = data['type']
        if note_type == TYPE_SINGLE:
            return NoteMeta(
                data['type'],
                data['lane'],
                data['beat'],
                data.get("flick", False)
            )
        elif note_type == TYPE_SLIDE:
            return NoteMeta(
                data['type'],
                INT_UNINITIALIZED,
                FLOAT_UNINITIALIZED,
                connections=[NoteConnection(j['beat'], j['lane']) for j in data['connections']]
                if data.get('connections', None) is not None else None
            )


class Note:
    TAP: int = 0
    FLICK: int = 1
    SLIDE: int = 2

    def __init__(self, meta: NoteMeta | None):
        self.__next: Note | None = None
        self.__type: int = INT_UNINITIALIZED
        self.__lane: int = INT_UNINITIALIZED
        self.__beat: float = FLOAT_UNINITIALIZED
        self.x: int = INT_UNINITIALIZED
        self.y: int = INT_UNINITIALIZED
        self.dead: bool = False
        self.init(meta)

    @staticmethod
    def getType(meta: NoteMeta) -> int:
        if meta.type == TYPE_SINGLE:
            if meta.flick:
                return Note.FLICK
            else:
                return Note.TAP
        elif meta.type == TYPE_SLIDE:
            return Note.SLIDE
        else:
            raise Exception("Unknown type: %s" % meta.type)

    def init(self, meta: NoteMeta | None):
        if meta is None:
            return
        self.__lane = meta.lane
        self.__beat = meta.beat
        self.__type = self.getType(meta)
        if self.type == self.SLIDE:
            self.__beat = FLOAT_UNINITIALIZED
            self.__make_connections(meta)

    def __make_connections(self, meta: NoteMeta | None):
        self.__next = None
        prev: Note | None = None
        for i in meta.connections:
            note = Note(None)
            note.__next = None
            if prev is not None:
                prev.__next = note
            else:
                self.__next = note
            note.__type = Note.SLIDE
            note.__beat = i.beat
            note.__lane = i.lane
            prev = note

    @property
    def type(self) -> int:
        return self.__type

    @property
    def next(self):
        return self.__next

    @property
    def lane(self) -> int:
        return self.__lane

    @property
    def progress(self):
        return self.__beat

    @lane.setter
    def lane(self, value):
        self.__lane = value


class NoteMap:

    def __init__(self):
        self.bpm: BPM | None = None
        self.notes: list[NoteMeta] = list()

    @staticmethod
    def load(path):
        self = NoteMap()
        with open(path, 'r', encoding='utf-8') as f:
            for i in json.load(f):
                if i['type'] == TYPE_BPM:
                    self.bpm = BPM.from_json(i)
                else:
                    self.notes.append(NoteMeta.from_json(i))
        return self

    def save(self, path):
        data = [self.bpm.json]
        for i in self.notes:
            data.append(i.json)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    @property
    def json(self) -> list[dict]:
        return [
            self.bpm.json,
            *[i.json for i in self.notes]
        ]


if __name__ == '__main__':
    noteMap = NoteMap.load("data/bokuha.json")
    print(noteMap.json)
