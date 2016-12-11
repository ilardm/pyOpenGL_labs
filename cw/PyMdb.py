# -*- coding: utf-8 -*-


import csv, pyodbc
from OpenGL import GL, GLU, GLUT


WINDOW_SIZE = (640, 480)
LINES_POINTS = []
INITIAL_TRANS = [0, 0]
INITIAL_SCALE = 1.0

scene_trans = INITIAL_TRANS.copy()
scene_scale = INITIAL_SCALE


def initOpenGL(argv):
    GLUT.glutInit(argv)
    GLUT.glutInitDisplayMode(GLUT.GLUT_SINGLE | GLUT.GLUT_RGB)
    GLUT.glutInitWindowPosition(0, 0)
    GLUT.glutInitWindowSize(*WINDOW_SIZE)
    GLUT.glutCreateWindow(b'cw')

    GL.glClearColor(1, 1, 1, 0)

    GL.glViewport(0, 0, *WINDOW_SIZE)
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GLU.gluOrtho2D(0, WINDOW_SIZE[0], 0, WINDOW_SIZE[1])
    GL.glMatrixMode(GL.GL_MODELVIEW)

    GLUT.glutDisplayFunc(draw_scene)
    GLUT.glutSpecialFunc(special_keys)
    GLUT.glutMainLoop()


def special_keys(key, *_):
    global scene_trans, scene_scale

    if key == GLUT.GLUT_KEY_UP:
        scene_trans[1] += (WINDOW_SIZE[1] * scene_scale * 0.1)
    elif key == GLUT.GLUT_KEY_DOWN:
        scene_trans[1] -= (WINDOW_SIZE[1] * scene_scale * 0.1)
    elif key == GLUT.GLUT_KEY_RIGHT:
        scene_trans[0] += (WINDOW_SIZE[0] * scene_scale * 0.1)
    elif key == GLUT.GLUT_KEY_LEFT:
        scene_trans[0] -= (WINDOW_SIZE[0] * scene_scale * 0.1)
    elif key == GLUT.GLUT_KEY_PAGE_UP:
        scene_scale += 0.05
    elif key == GLUT.GLUT_KEY_PAGE_DOWN:
        scene_scale = max(0, scene_scale - 0.05)
    elif key == GLUT.GLUT_KEY_HOME:
        scene_trans = INITIAL_TRANS.copy()
        scene_scale = INITIAL_SCALE

    print('scale:', scene_scale, 'trans:', scene_trans)

    GLUT.glutPostRedisplay()


def prepare_scene(path):
    import pprint

    global LINES_POINTS

    LINES_POINTS = path.GetPoints()

    print('LINES_POINTS:')
    pprint.pprint(LINES_POINTS)


def draw_scene():
    global scene_trans, scene_scale, LINES_POINTS

    GL.glClear(GL.GL_COLOR_BUFFER_BIT)
    GL.glLoadIdentity()

    GL.glPushMatrix()

    GL.glTranslatef(scene_trans[0], scene_trans[1], 0)
    GL.glScale(scene_scale, scene_scale, scene_scale)

    GL.glColor3f(0, 0, 0)
    GL.glBegin(GL.GL_LINES)

    for pt in LINES_POINTS:
        GL.glVertex2f(*pt)

    GL.glEnd()

    GL.glPopMatrix()

    GL.glFlush()


class path:
    '''Это контур и работа с ним'''
    def __init__(self):
        self._segments=[]

    def Add(self,seg):
        '''Добавить сегмент в контур'''
        self._segments.append(seg)
        return

    def GetPoints(self):
        pts = []

        for seg in self._segments:
            pts += seg.GetPoints()

        return pts


class point:
    '''Это класс точка'''
    def __init__(self,x=0,y=0):
        self._x=x
        self._y=y

    def Set(self,x,y):
        self._x=x
        self._y=y

    def Get(self):
        return (self._x,self._y)

    def __str__(self):
        return '(%r, %r)' % (self._x, self._y)

class database():
    '''Этот класс читает данные из базы'''

    def GetFromBase(self,pathdb, path,unitpos):
        '''Читает набор точек из pathdb контура path панели unitpos
        paramID, UnitPos, HoldTable, Hold1, Hold2, hold3, ParamName, ParamType, NumValue, StrValue
        '''
        # DRV = '{Microsoft Access Driver (*.mdb)}'
        DRV = '{Microsoft Access Driver (*.mdb, *.accdb)}'
        PWD = ''

        # connect to db
        con = pyodbc.connect('DRIVER={};DBQ={};PWD={}'.format(DRV,pathdb,PWD))
        cur = con.cursor()

        # run a query and get the results
        sqlstr='''SELECT Hold1, Hold2, hold3, ParamName, NumValue FROM TParams,TPaths WHERE HoldTable='TPaths' AND TParams.UnitPos={}
 AND TParams.Hold1=TPaths.PathID AND TPaths.PanelPos=TParams.UnitPos AND IsTCuts=0 AND
 TPaths.PathID={} AND Hold2>0 ORDER BY ParamID'''.format(unitpos, path)
        rows = cur.execute(sqlstr).fetchall()   # здесь у нас вообще все подряд параметры
        cur.close()
        con.close()
        return rows

class segment:
    '''Это сегмент контура'''
    pass

class linesegment (segment):
    '''Это сегмент отрезок'''
    def __init__(self,beg=point(0,0),end=point(0,0)):
        self._beg=beg
        self._end=end

    def Set(self,beg=point(0,0),end=point(0,0)):
        self._beg=beg
        self._end=end

    def Get(self):
        return (self._beg,self._end)

    def GetPoints(self):
        return (self._beg.Get(), self._end.Get())

    def __str__(self):
        return 'line %s -> %s' % (self._beg, self._end)

class arcsegment (segment):
    '''Это сегмент дуга'''
    def __init__(self,beg=point(0,0),end=point(0,0), mid=point(0,0)):
        self._beg=beg
        self._end=end
        self._mid=mid

    def Set(self,beg=point(0,0),end=point(0,0), mid=point(0,0)):
        self._beg=beg
        self._end=end
        self._mid=mid

    def Get(self):
        return (self._beg,self._end, self._mid)

    def GetPoints(self):
        # FIXME: actually we need to build circle part from lines with
        # NVERT-1 lines but for simplicity lets assume NVERT=3 :P

        return (
            self._beg.Get(),
            self._mid.Get(),
            self._mid.Get(),
            self._end.Get()
        )

    def __str__(self):
        return 'arc %s -> %s -> %s' % (self._beg, self._mid, self._end)

class SegmentCreator:
    '''Это фабрика по созданию сегметнтов'''
    def CreateSegment(self, rows):
        '''По набору строк возвращаем сегмент нужного типа'''
        for coords in rows:      # Кординаты концов сегмента
            stype=coords[1]     # тип 1 - отрезок, 2 - дуга
            varariable=coords[3]    # Имя параметра
            globals()[varariable]=coords[4]  # Создаем перменную с именем параметра
        if (stype==1):  # Отрезок
            seg=linesegment(point(X1,Y1),point(X2,Y2))
        elif (stype==2):    # Дуга
            seg=arcsegment(point(X1,Y1), point(X2,Y2), point(XM,YM))
        else:   # Не пойми что
            seg=None
            assert(True)
        print('created', str(seg))
        return seg

    def ParseRows(self,rows):
        '''По набору строк rows возвращает набор строк со строками для одного сегмента'''
        lines=[]    # Набор строк со строками одного сегмента - контур целиком. Возвращаемое значение
        line=[]     # Строка с данными для одного сегмента
        hold3=1     # Первый сегмент - всегда единица
        for row in rows:            # Организуем цикл по строкам из базы данных
            if hold3!=row[2]:       # Если запись относится к рассматриваемому сегменту
                lines.append(line)  # прочитанные данные помещаем в выходное значение
                line=[]             # Обнуляем данные по сегменту
            line.append(row)    # Добавляем данные
            hold3=row[2]            # А здесь хранится номер рассматриваемого сегмента
        lines.append(line)
        return lines

def main(argv):
# set up some constants

  import os.path

  global LINES_POINTS

  MDB = argv[1]
  assert(os.path.exists(MDB))
  MDB = os.path.abspath(MDB)

  DRV = '{Microsoft Access Driver (*.mdb)}'
  PWD = ''

  PanelPos=int(argv[2])        # Номер панели (PanelPos в таблице TPaths)
  PathPos=1         # Номер контура (PathID в таблице TPaths)
  base=database()
  rows=base.GetFromBase(MDB,PathPos,PanelPos)

  sg=SegmentCreator()
  lines=sg.ParseRows(rows)
  pat=path()
  for line in lines:
    seg=sg.CreateSegment(line)
    pat.Add(seg)

  prepare_scene(pat)
  initOpenGL(argv)

if __name__ == '__main__':
    import sys

    main(sys.argv)
