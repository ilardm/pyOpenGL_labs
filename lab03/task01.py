#-*- coding: utf-8

# see NeHe tutorials
# http://nehe.gamedev.net/tutorial/3d_shapes/10035/

from OpenGL import GL, GLU, GLUT


WINDOW_SIZE = (640, 480)
LIGHT_POS = (900.0, 900.0, 900.0, 1.0)
LIGHT_COLOR = '#ffffff'
HOME_COLOR = '#ffffff'
ROOF_COLOR = '#ffffff'
GROUND_COLOR = '#663300'
HOME_WIDTH = 3.0
HOME_HEIGHT = 3.0
HOME_DEPTH = 4.0
TEX_HOME_WIDTH = 0.5
TEX_HOME_HEIGHT = 0.25
ROOF_HEIGHT = HOME_HEIGHT * 0.45
TEX_ROOF_WIDTH = TEX_HOME_WIDTH / 2.0
GROUND = -1 * (HOME_HEIGHT + ROOF_HEIGHT) / 2.0
FPS = 60

scene_rot = (0.0, 0.0)  # x/z rot
textures = []


def hex2rgb(hexstr):
    hexstr = hexstr.strip('#')
    intval = 0

    try:
        intval = int(hexstr, 16)
    except ValueError:
        intval = 0

    rgb = []
    for shift in (16, 8, 0):
        value = (intval >> shift) & 0xff
        value /= 255.0
        rgb.append(value)

    return rgb


def init(argv):
    from PIL import Image
    global textures

    GL.glClearColor(0.5, 0.5, 0.5, 1)

    GL.glEnable(GL.GL_LIGHTING)
    GL.glEnable(GL.GL_LIGHT0)
    GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, LIGHT_POS)
    GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, hex2rgb(LIGHT_COLOR))

    GL.glClearDepth(1.0)
    GL.glDepthFunc(GL.GL_LEQUAL)
    GL.glEnable(GL.GL_DEPTH_TEST)

    # http://pyopengl.sourceforge.net/context/tutorials/nehe7.html
    img = Image.open(argv[1])
    img = img.convert('RGBA')
    img_data = img.tobytes('raw', 'RGBA', 0, -1)
    GL.glHint(GL.GL_PERSPECTIVE_CORRECTION_HINT, GL.GL_NICEST)
    textures.append(GL.glGenTextures(1))
    GL.glBindTexture(GL.GL_TEXTURE_2D, textures[0])
    GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, img.size[0], img.size[1], 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, img_data)
    GL.glEnable(GL.GL_TEXTURE_2D)

    GL.glViewport(0, 0, *WINDOW_SIZE)
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GLU.gluPerspective(60, float(WINDOW_SIZE[0])/float(WINDOW_SIZE[1]), 0.1, 100)
    GL.glMatrixMode(GL.GL_MODELVIEW)


def draw_home_box():
    GL.glPushMatrix()

    # translate to left bottom home box corner
    GL.glTranslatef(-1*HOME_WIDTH/2.0, -1*HOME_DEPTH/2.0, GROUND)

    GL.glBegin(GL.GL_QUADS)

    # draw all sides in CCW direction from bottom left corner having
    # N-vector directed outside the home

    GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_DIFFUSE, hex2rgb(GROUND_COLOR))

    # floor
    GL.glVertex3f(0,            0,              0)
    GL.glVertex3f(0,            HOME_DEPTH,     0)
    GL.glVertex3f(HOME_WIDTH,   HOME_DEPTH,     0)
    GL.glVertex3f(HOME_WIDTH,   0,              0)

    GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_DIFFUSE, hex2rgb(HOME_COLOR))

    # front wall
    GL.glTexCoord2f(0.0,            0.5);                   GL.glVertex3f(0,            0,              0)
    GL.glTexCoord2f(TEX_HOME_WIDTH, 0.5);                   GL.glVertex3f(HOME_WIDTH,   0,              0)
    GL.glTexCoord2f(TEX_HOME_WIDTH, 0.5 + TEX_HOME_HEIGHT); GL.glVertex3f(HOME_WIDTH,   0,              HOME_HEIGHT)
    GL.glTexCoord2f(0.0,            0.5 + TEX_HOME_HEIGHT); GL.glVertex3f(0,            0,              HOME_HEIGHT)

    # back wall
    GL.glTexCoord2f(0.0,            0.0);                   GL.glVertex3f(HOME_WIDTH,   HOME_DEPTH,     0)
    GL.glTexCoord2f(TEX_HOME_WIDTH, 0.0);                   GL.glVertex3f(0,            HOME_DEPTH,     0)
    GL.glTexCoord2f(TEX_HOME_WIDTH, TEX_HOME_HEIGHT);       GL.glVertex3f(0,            HOME_DEPTH,     HOME_HEIGHT)
    GL.glTexCoord2f(0.0,            TEX_HOME_HEIGHT);       GL.glVertex3f(HOME_WIDTH,   HOME_DEPTH,     HOME_HEIGHT)

    # right wall
    GL.glTexCoord2f(TEX_HOME_WIDTH, 0.5);                   GL.glVertex3f(HOME_WIDTH,   0,              0)
    GL.glTexCoord2f(1.0,            0.5);                   GL.glVertex3f(HOME_WIDTH,   HOME_DEPTH,     0)
    GL.glTexCoord2f(1.0,            0.5 + TEX_HOME_HEIGHT); GL.glVertex3f(HOME_WIDTH,   HOME_DEPTH,     HOME_HEIGHT)
    GL.glTexCoord2f(TEX_HOME_WIDTH, 0.5 + TEX_HOME_HEIGHT); GL.glVertex3f(HOME_WIDTH,   0,              HOME_HEIGHT)

    # left wall
    GL.glTexCoord2f(TEX_HOME_WIDTH, 0.0);                   GL.glVertex3f(0,            HOME_DEPTH,     0)
    GL.glTexCoord2f(1.0,            0.0);                   GL.glVertex3f(0,            0,              0)
    GL.glTexCoord2f(1.0,            TEX_HOME_HEIGHT);       GL.glVertex3f(0,            0,              HOME_HEIGHT)
    GL.glTexCoord2f(TEX_HOME_WIDTH, TEX_HOME_HEIGHT);       GL.glVertex3f(0,            HOME_DEPTH,     HOME_HEIGHT)

    GL.glEnd()
    GL.glPopMatrix()


def draw_home_roof():
    GL.glPushMatrix()

    # translate to left bottom roof corner
    GL.glTranslatef(-1*HOME_WIDTH/2.0, -1*HOME_DEPTH/2.0, GROUND+HOME_HEIGHT)

    GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_DIFFUSE, hex2rgb(ROOF_COLOR))

    # draw all roof sides in CCW direction from bottom left corner having
    # N-vector directed outside the home

    roof_center = HOME_WIDTH / 2.0

    GL.glBegin(GL.GL_QUADS)

    # righ part of the roof
    GL.glTexCoord2f(TEX_HOME_WIDTH, 0.5 + TEX_HOME_HEIGHT); GL.glVertex3f(HOME_WIDTH,   0,              0)
    GL.glTexCoord2f(1.0,            0.5 + TEX_HOME_HEIGHT); GL.glVertex3f(HOME_WIDTH,   HOME_DEPTH,     0)
    GL.glTexCoord2f(1.0,            1.0);                   GL.glVertex3f(roof_center,  HOME_DEPTH,     ROOF_HEIGHT)
    GL.glTexCoord2f(TEX_HOME_WIDTH, 1.0);                   GL.glVertex3f(roof_center,  0,              ROOF_HEIGHT)

    # left part of the roof
    GL.glTexCoord2f(TEX_HOME_WIDTH, TEX_HOME_HEIGHT);       GL.glVertex3f(0,            HOME_DEPTH,     0)
    GL.glTexCoord2f(1.0,            TEX_HOME_HEIGHT);       GL.glVertex3f(0,            0,              0)
    GL.glTexCoord2f(1.0,            0.5);                   GL.glVertex3f(roof_center,  0,              ROOF_HEIGHT)
    GL.glTexCoord2f(TEX_HOME_WIDTH, 0.5);                   GL.glVertex3f(roof_center,  HOME_DEPTH,     ROOF_HEIGHT)

    GL.glEnd()

    GL.glBegin(GL.GL_TRIANGLES)

    # front side of the roof
    GL.glTexCoord2f(0.0,            0.5 + TEX_HOME_HEIGHT); GL.glVertex3f(0,            0,              0)
    GL.glTexCoord2f(TEX_HOME_WIDTH, 0.5 + TEX_HOME_HEIGHT); GL.glVertex3f(HOME_WIDTH,   0,              0)
    GL.glTexCoord2f(TEX_ROOF_WIDTH, 1.0);                   GL.glVertex3f(roof_center,  0,              ROOF_HEIGHT)

    # back side of the roof
    GL.glTexCoord2f(0.0,            TEX_HOME_HEIGHT);       GL.glVertex3f(HOME_WIDTH,   HOME_DEPTH,     0)
    GL.glTexCoord2f(TEX_HOME_WIDTH, TEX_HOME_HEIGHT);       GL.glVertex3f(0,            HOME_DEPTH,     0)
    GL.glTexCoord2f(TEX_ROOF_WIDTH, 0.5);                   GL.glVertex3f(roof_center,  HOME_DEPTH,     ROOF_HEIGHT)

    GL.glEnd()

    GL.glPopMatrix()


def draw_scene():
    global scene_rot

    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    # reset view to (0, 0, 0):
    #  y ^
    #    |
    #    |
    #    |
    #    |
    #   _|_
    #  /   \
    # |  *  |--------->
    #  \___/          x
    # z
    GL.glLoadIdentity()


    # 'zoom out' the scene
    GL.glTranslatef(0, 0, -1 * HOME_HEIGHT * 3)

    # rotate world so it would be faced:
    #  z ^
    #    |
    #    |
    #    |
    #    |
    #   _|_
    #  /   \
    # |  x  |--------->
    #  \___/          x
    # y
    GL.glRotatef(-90, 1, 0, 0)

    # save rotation/position and reset to initial values
    GL.glPushMatrix()

    # rotate, scale entire scene
    GL.glRotatef(scene_rot[0], 1, 0, 0)
    GL.glRotatef(scene_rot[1], 0, 0, 1)

    draw_home_box()
    draw_home_roof()

    # load saved earlier rotation/position
    GL.glPopMatrix()

    GLUT.glutSwapBuffers()


def special_keys(key, *_):
    global scene_rot

    if key == GLUT.GLUT_KEY_UP:
        scene_rot = (scene_rot[0] - 10, scene_rot[1])
    elif key == GLUT.GLUT_KEY_DOWN:
        scene_rot = (scene_rot[0] + 10, scene_rot[1])
    elif key == GLUT.GLUT_KEY_RIGHT:
        scene_rot = (scene_rot[0], scene_rot[1] - 10)
    elif key == GLUT.GLUT_KEY_LEFT:
        scene_rot = (scene_rot[0], scene_rot[1] + 10)

    GLUT.glutPostRedisplay()


def main(argv):
    GLUT.glutInit(argv)
    GLUT.glutInitDisplayMode(GLUT.GLUT_DOUBLE | GLUT.GLUT_RGB)
    GLUT.glutInitWindowPosition(0, 0)
    GLUT.glutInitWindowSize(*WINDOW_SIZE)
    GLUT.glutCreateWindow(b'lab03.task01')

    init(argv)

    GLUT.glutDisplayFunc(draw_scene)
    GLUT.glutSpecialFunc(special_keys)
    GLUT.glutMainLoop()

if __name__ == '__main__':
    import sys

    main(sys.argv)
