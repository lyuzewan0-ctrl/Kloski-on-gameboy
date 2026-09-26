"""Create the redesigned report without modifying the original project files.

Run from any directory: python tools/build_report.py
Requires the packages in tools/requirements-report.txt.
"""
from pathlib import Path
import os
from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "klotski-report-redesigned.pdf"
ASSETS = ROOT / "docs" / "assets"
W, H = 595.276, 841.89
INK = HexColor("#162E29")
GREEN = HexColor("#42694C")
MUTED = HexColor("#65746C")
PALE = HexColor("#E8EEE1")
PAPER = HexColor("#FAFBF7")
LINE = HexColor("#D6DFD0")
ACCENT = HexColor("#C8D987")
MONO = "Courier"
SANS = "Helvetica"
BOLD = "Helvetica-Bold"


def fonts():
    global SANS, BOLD, MONO
    candidates = [
        (Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts", "arial.ttf", "arialbd.ttf", "consola.ttf"),
        (Path("/usr/share/fonts/truetype/dejavu"), "DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSansMono.ttf"),
    ]
    for base, regular, bold, mono in candidates:
        if all((base / f).exists() for f in [regular, bold, mono]):
            for name, file in [("ReportSans", regular), ("ReportBold", bold), ("ReportMono", mono)]:
                pdfmetrics.registerFont(TTFont(name, str(base / file)))
            SANS, BOLD, MONO = "ReportSans", "ReportBold", "ReportMono"
            pdfmetrics.registerFontFamily(SANS, normal=SANS, bold=BOLD, italic=SANS, boldItalic=BOLD)
            return


def extract_figures():
    ASSETS.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(ROOT / "report.pdf")
    for page, name in [(1, "original-board.png"), (2, "original-selection-case.png")]:
        list(reader.pages[page].images)[0].image.save(ASSETS / name)


class Report:
    def __init__(self):
        OUT.parent.mkdir(parents=True, exist_ok=True)
        self.c = canvas.Canvas(str(OUT), pagesize=(W, H), pageCompression=1)
        self.c.setTitle("Kloski on gameboy | Redesigned Klotski project report")
        self.c.setAuthor("Zewan Lyu; Zeyan YIN; Weihan Li; Xiang Li")
        self.c.setSubject("Editorial redesign of the original report dated 2025-01-06")
        self.page = 0

    def rect(self, x, y, w, h, fill, radius=0, stroke=None):
        c = self.c
        c.setFillColor(fill)
        c.setStrokeColor(stroke or fill)
        if radius:
            c.roundRect(x, H-y-h, w, h, radius, fill=1, stroke=bool(stroke))
        else:
            c.rect(x, H-y-h, w, h, fill=1, stroke=bool(stroke))

    def text(self, s, x, y, size=11, font=None, color=INK):
        self.c.setFillColor(color)
        self.c.setFont(font or SANS, size)
        self.c.drawString(x, H-y-size*.82, s)

    def para(self, s, x, y, w, size=10.4, color=INK, leading=None):
        style = ParagraphStyle("body", fontName=SANS, fontSize=size,
                               leading=leading or size*1.48, textColor=color)
        p = Paragraph(s, style)
        _, h = p.wrap(w, 900)
        assert y+h < H-44, (self.page, y, h, s[:90])
        p.drawOn(self.c, x, H-y-h)
        return y+h

    def heading(self, number, title, y):
        self.text(number, 44, y+2, 10, BOLD, GREEN)
        self.text(title, 78, y, 17, BOLD)
        return y+31

    def line(self, x1, y1, x2, y2, color=LINE, width=1):
        c=self.c
        c.setStrokeColor(color)
        c.setLineWidth(width)
        c.line(x1,H-y1,x2,H-y2)

    def arrow(self, points, color=GREEN, width=1.5):
        import math
        for a,b in zip(points,points[1:]): self.line(*a,*b,color,width)
        a,b=points[-2:]
        angle=math.atan2(b[1]-a[1],b[0]-a[0])
        for d in [-.52,.52]:
            self.line(b[0],b[1],b[0]-7*math.cos(angle+d),b[1]-7*math.sin(angle+d),color,width)

    def image(self, name, x, y, w, h):
        self.c.drawImage(str(ASSETS/name), x, H-y-h, w,h, mask="auto")

    def new(self, label, title, subtitle=""):
        if self.page: self.c.showPage()
        self.page += 1
        self.rect(0,0,W,H,PAPER)
        self.text("KLOSKI ON GAMEBOY",44,26,8.5,BOLD,GREEN)
        self.text(label.upper(),357,26,8.5,SANS,MUTED)
        self.line(44,47,551,47)
        self.text(title,44,68,28,BOLD)
        if subtitle: self.para(subtitle,44,108,505,10,MUTED)
        self.line(44,792,551,792)
        self.text("Original report: 06 Jan 2025  /  Redesigned edition",44,806,8,SANS,MUTED)
        self.text(f"{self.page:02d} / 08",508,805,9,BOLD,GREEN)
        self.c.bookmarkPage(f"page{self.page}")
        self.c.addOutlineEntry(title,f"page{self.page}",0,False)

    def note(self, title, body, y, height=75):
        self.rect(44,y,507,height,PALE,7)
        self.text(title,59,y+13,10,BOLD,GREEN)
        self.para(body,59,y+31,477,9.4)

    def save(self): self.c.save()


def create():
    fonts()
    extract_figures()
    r=Report()

    # 1. Cover and navigation.
    r.new("Project report", "Kloski on gameboy")
    r.rect(0,48,W,446,INK)
    r.text("DIGITAL SYSTEM AND COMPUTER STRUCTURE",44,74,9,BOLD,ACCENT)
    r.text("Kloski",43,120,62,BOLD,white)
    r.text("on gameboy",44,188,45,BOLD,white)
    r.para("A redesigned edition of<br/><b>A Report of Team Project: Klotski on Game Boy</b>",46,258,290,11,white)
    r.text("A sliding-block puzzle, built in assembly.",46,324,12,SANS,ACCENT)
    r.text("08",46,370,33,BOLD,white)
    r.text("LEVELS",47,411,8,BOLD,ACCENT)
    r.text("04 x 05",147,370,33,BOLD,white)
    r.text("PLAYABLE CELLS",148,411,8,BOLD,ACCENT)
    r.text("01",304,370,33,BOLD,white)
    r.text("ESCAPE GOAL",305,411,8,BOLD,ACCENT)
    r.image("original-board.png",398,267,135,168.25)
    r.text("Original project artwork",399,446,7.5,SANS,ACCENT)
    r.text("THE TEAM",44,519,9,BOLD,GREEN)
    authors=[("Zewan Lyu","999019888"),("Zeyan YIN","999020183"),("Weihan Li","999019797"),("Xiang Li","999019771")]
    for i,(name,sid) in enumerate(authors):
        x=44+i*130
        r.text(name,x,545,12,BOLD)
        r.text(sid,x,565,9,SANS,MUTED)
    r.text("Mathematics with Computer Science",44,599,10,SANS,MUTED)
    r.line(44,627,551,627)
    topics=[("02","Play & controls"),("03","Graphics & VBlank"),("04","Board & byte model"),
            ("05","Encoded example"),("06","Select & slide"),("07","Rendering pipeline"),("08","States & optimization")]
    for i,(num,title) in enumerate(topics):
        x=44+(i%2)*264; y=649+(i//2)*25
        r.text(num,x,y,9,BOLD,GREEN);r.text(title,x+27,y,10)
        r.c.linkRect("",f"page{int(num)}",(x,H-y-15,x+235,H-y+2),relative=0,thickness=0)
    r.para("Original authorship and technical intent are retained. This edition refines language, layout and diagrams; code-aware clarifications are labeled.",44,758,505,8.2,MUTED)

    # 2. Introduction and controls.
    r.new("01 / 02  Game & input", "Play & controls", "Six Game Boy buttons. Two interaction modes. One escape route.")
    y=r.heading("1", "Introduction",151)
    y=r.para("This Game Boy adaptation of Klotski offers eight levels, designed with increasing difficulty. Players choose a level from the menu, then rearrange nine smaller blocks and the large, distinctively patterned main character, Cao Cao.",44,y,507)
    y=r.para("The objective is to bring Cao Cao to the bottom-center exit of the 4-column by 5-row board. Empty cells provide room to maneuver. Blocks may slide only where there is enough free space; they cannot overlap or cross the surrounding wall.",44,y+10,507)
    y=r.heading("2", "Keys",y+28)
    r.para("The controls below refer to Game Boy buttons. The original project uses Emulicious; its reported keyboard mapping is <b>S = Game Boy A</b>, <b>A = Game Boy B</b>, plus the arrow keys. Check the emulator's input settings if your mapping differs.",44,y,507)
    top=398
    cols=[44,151,353]; widths=[107,202,198]
    for x,w,label in zip(cols,widths,["CONTEXT","DIRECTION PAD","A / B BUTTONS"]):
        r.rect(x,top,w,29,INK);r.text(label,x+11,top+10,8,BOLD,white)
    rows=[("Menu","Choose one of eight levels.","A: load the selected level."),
          ("Selecting","Choose the closest block in a direction.","A: enter moving mode.\nB: return to the menu."),
          ("Moving","Slide the selected block into free space.","A: finish and select again.\nB: return to the menu."),
          ("Victory","-","A: return to the menu.")]
    for i,row in enumerate(rows):
        yy=top+29+i*53
        r.rect(44,yy,507,53,PALE if i%2==0 else white)
        for j,txt in enumerate(row):r.para(escape(txt).replace("\n","<br/>"),cols[j]+11,yy+10,widths[j]-22,9.3)
    r.note("2.1  In a level", "Choose a block with the direction pad, press A, slide it, then press A again to finish. Press B to return to the menu; re-entering a level starts it again.",655,72)
    r.para("<b>2.2  In the menu:</b> choose a level with the direction pad, then press A. <b>Code clarification:</b> the win check runs in selecting mode; victory opens a screen where A returns to the menu.",44,744,507,9.2)

    # 3. Graphics.
    r.new("03  Graphics", "Drawing within VBlank", "The board is rendered through the background tile map.")
    y=r.heading("3.1", "Block size",151)
    y=r.para("Each Game Boy tile is 8 x 8 pixels. The visible screen contains 20 columns by 18 rows of tiles. Fitting a 4 x 5 Klotski board into that space allows each smallest square cell to occupy at most 3 x 3 tiles. A selected block is shown by reversing its colors.",44,y,507)
    for x,num,label in [(44,"8 x 8","PIXELS PER TILE"),(217,"3 x 3","TILES PER CELL"),(390,"180","BOARD TILES")]:
        r.rect(x,274,161,89,PALE,7);r.text(num,x+16,290,29,BOLD,GREEN);r.text(label,x+16,337,8,BOLD,MUTED)
    y=r.heading("3.2", "Block update",394)
    y=r.para("The board can span 180 background tiles. OAM supports only 40 sprite entries, so the board is drawn by modifying the background during VBlank. As with shadowOAM, the program prepares changes in a WRAM buffer, <b>shadowSCRN</b>, and copies selected regions into screen memory.",44,y,507)
    y=r.para("Changing a selected block can affect a large region. Even updating only the board area may exceed a single VBlank. Splitting the work across two VBlanks is possible, but the original design avoids that delay by recording the affected region and choosing a transfer routine according to its height.",44,y+11,507)
    for x,top,bottom in [(44,"Compare","old / new matrices"),(217,"Prepare","shadowSCRN in WRAM"),(390,"Transfer","changed region in VRAM")]:
        r.rect(x,593,161,67,INK,6)
        r.text(top,x+14,607,13,BOLD,white);r.text(bottom,x+14,633,8,SANS,ACCENT)
    r.arrow([(205,626),(215,626)]);r.arrow([(378,626),(388,626)])
    r.note("Timing strategy", "The region recorded during matrix comparison determines the update height. During VBlank, shorterFunction or higherFunction performs the screen transfer; loop expansion reduces transfer overhead.",697,77)

    # 4. Board storage.
    r.new("04  Sliding blocks", "A board in 42 bytes", "The logical board and its surrounding wall share a compact matrix.")
    y=r.heading("4.1", "State of the coordinates",151)
    y=r.para("Treat each smallest square as an integer coordinate. A cell is either free or occupied. Before a slide, the program checks the destination cells in the chosen direction. A valid move updates both the block position and cell occupancy; an occupied target makes the move invalid.",44,y,507)
    y=r.para("Initial configurations are stored in ROM as 7 x 6 matrices. The playable area is 5 rows by 4 columns; a one-cell-thick wall surrounds it. At level entry, the configuration is copied into WRAM.",44,y+10,507)
    y=r.heading("4.2", "Matrix configuration",y+24)
    y=r.para("Each matrix element is one byte. Its upper four bits encode the block type, bit 2 marks selection, and the lowest two bits identify the cell's position within a block. Bit 3 is not assigned a role in the original report.",44,y,507)
    for i in range(8):
        x=44+i*63.4
        fill=GREEN if i<4 else (LINE if i==4 else (INK if i==5 else PALE))
        r.rect(x,421,59,51,fill,4)
        r.text(str(7-i),x+24,435,19,BOLD,white if i<4 or i==5 else INK)
    r.text("BLOCK TYPE",95,484,9,BOLD,GREEN)
    r.text("UNUSED",299,484,8,SANS,MUTED)
    r.text("SELECT",365,484,8,BOLD,GREEN)
    r.text("BLOCK PART",459,484,8,BOLD,GREEN)
    r.text("HIGH NIBBLE",44,528,9,BOLD,GREEN)
    types=[("0","Empty cell"),("1","1 x 1 square"),("2","2 x 1 horizontal block"),("3","1 x 2 vertical block"),("4","2 x 2 main character"),("5","Wall")]
    for i,(val,label) in enumerate(types):
        yy=553+i*27;r.text(val,44,yy,10,MONO,GREEN);r.text(label,72,yy,10)
    r.text("LOW TWO BITS",331,528,9,BOLD,GREEN)
    for i,(val,label) in enumerate([("00","Top left"),("01","Top right"),("10","Bottom left"),("11","Bottom right")]):
        yy=553+i*27;r.text(val,331,yy,10,MONO,GREEN);r.text(label,369,yy,10)
    r.para("Type dimensions follow the supplied code; the original report identifies types 1-4 without listing their dimensions.",331,673,214,8.8,MUTED)
    r.para("The selected block is tracked by the matrix index of its top-left cell. Selection flags are applied to the cells belonging to that block.",44,742,507,9.2)

    # 5. Example preserved from the report, not replaced by today's level 1.
    r.new("04  Encoding example", "From bytes to blocks", "The original report's example, preserved as an illustration.")
    r.text("4.2  EXAMPLE CONFIGURATION",44,151,10,BOLD,GREEN)
    r.para("The excerpt below reproduces the original example, including its <b>level1</b> label. The selected top-left square has bit 2 set: <b>%00010100</b>. The surrounding wall is encoded as <b>%01010000</b>.",44,178,507)
    code=['SECTION "Configurations", ROM0','level1:',
          'DB %01010000,%01010000,%01010000,%01010000,%01010000,%01010000',
          'DB %01010000,%00010100,%00100000,%00100001,%00010000,%01010000',
          'DB %01010000,%00110000,%01000000,%01000001,%00110000,%01010000',
          'DB %01010000,%00110010,%01000010,%01000011,%00110010,%01010000',
          'DB %01010000,%00110000,%00010000,%00010000,%00110000,%01010000',
          'DB %01010000,%00110010,%00000000,%00000000,%00110010,%01010000',
          'DB %01010000,%01010000,%01010000,%01010000,%01010000,%01010000']
    r.rect(44,244,507,169,INK,7)
    for i,line in enumerate(code):r.text(line,57,258+i*16.6,8.15,MONO,white)
    r.image("original-board.png",62,445,195,243.03)
    r.text("FIG. 1",290,450,9,BOLD,GREEN)
    y=r.para("The example board from the original report. The dark square at the top left is selected; the main character occupies a 2 x 2 area. Two empty cells appear at the bottom center.",290,475,254,10.2)
    y=r.para("At initialization, every cell of <b>oldMatrix</b> is set to the wall byte. <b>newMatrix</b> receives the ROM configuration. The matrix-to-screen procedure compares the two to display the initial board.",290,y+19,254,10.2)
    r.note("Editorial clarification", "The current data.inc uses a different configuration for level1. This example is retained from report.pdf and is not presented as a screenshot of the supplied ROM's first level.",718,62)

    # 6. Selection and movement.
    r.new("04  Interaction logic", "Select, validate, slide", "Selection and movement operate on the same matrix representation.")
    y=r.heading("4.3", "Selecting blocks",151)
    y=r.para("The selected block is identified by its top-left matrix position. Button A changes from selecting to moving; the <b>stateOffSet</b> variable determines which interaction loop runs. Otherwise, a direction key searches for the closest block in that direction.",44,y,507)
    y=r.para("For a block with a one-cell edge, the search checks one line. With a two-cell edge, it checks two lines and chooses the closest candidate. Four special-case routines handle corner arrangements that a straight-line search can miss.",44,y+9,507)
    r.rect(44,332,507,149,PALE,7)
    r.image("original-selection-case.png",60,349,145,112.26)
    r.text("FIG. 2  SELECTION EDGE CASE",226,350,9,BOLD,GREEN)
    r.para("In the example from the original report, a direct search can fail to reach the top-left block. The implementation adds checks for the top-left, top-right, bottom-left and bottom-right cases.",226,377,306,9.7)
    y=r.heading("4.4", "Moving blocks",503)
    y=r.para("A direction key requests a slide. The program checks for overlap, walls and sufficient free space before modifying the board. Button A returns to selecting mode. For a valid move, the block's old cells are cleared in <b>newMatrix</b>, then the block is copied from <b>oldMatrix</b> into its shifted position.",44,y,507)
    y=r.heading("4.5", "Forming the next matrix",y+24)
    r.para("<b>Valid selection or move:</b> copy the old matrix and modify the affected entries to represent the action.<br/><br/><b>Invalid action:</b> keep the old and new matrix contents equivalent, so the board does not change.",44,y,507)

    # 7. Rendering, menu and counters.
    r.new("04 / 05 / 06  Rendering", "One pipeline, many screens", "Matrix decoding connects the logical board to the visible tile map.")
    y=r.heading("4.6", "Matrix to shadowSCRN",151)
    y=r.para("The renderer scans <b>oldMatrix</b> and <b>newMatrix</b>. For each changed byte, it decodes the block type, block part and selection state. Two mappings connect a matrix cell to its graphics:",44,y,507)
    steps=[("01", "Position mapping", "MatrixToSCRNOffSetTable maps a matrix position to an offset in shadowSCRN. Each logical cell occupies a 3 x 3 tile region. Background rows use a 32-tile stride, although only 20 columns are visible."),
           ("02", "Byte decoding", "ByteDecoder maps the encoded value to the corresponding 3 x 3 tile-ID pattern and its selected state."),
           ("03", "Drawing and synchronization", "UnitDraw copies the tile pattern to the target buffer position. Changed regions are recorded, and the new matrix values are copied back into oldMatrix.")]
    yy=255
    for num,title,body in steps:
        r.rect(44,yy,31,28,GREEN,4);r.text(num,50,yy+8,11,BOLD,white)
        r.text(title,88,yy+1,12,BOLD)
        r.para(body,88,yy+23,461,9.9)
        yy+=102
    r.para("<b>Source clarification:</b> the original report names table.inc; the supplied project stores MatrixToSCRNOffSetTable in <b>data.inc</b>. The original 18 x 32 description covers the visible rows with the background's 32-column stride.",44,565,507,9,MUTED)
    y=r.heading("5", "Menu",630)
    r.para("The menu reuses the board's data structure and rendering functions. Its level choices are drawn in 3 x 3 tile units. A sprite pointer selects the level, and stateOffSet switches into the game after confirmation.",44,y,507,9.7)
    y=r.heading("6", "Game state counters",713)
    r.para("<b>LevelCounter</b> tracks the level (displayed as 1-8, stored as 0-7). The step count is kept in <b>stepCounterArray</b>, incremented by stepCounter, and displayed at the upper right; the level appears at the upper left. Both counters are stored in WRAM.",44,y,507,9.1)

    # 8. FSM and optimization.
    r.new("07 / 08  Control & performance", "State-driven, time-aware", "Five states organize the game; selective updates keep drawing focused.")
    y=r.heading("7", "Finite state machine",151)
    r.para("stateOffSet indexes the state table. The diagram redraws the original state machine and labels the level-loading transition explicitly.",44,y,507)
    def box(x,y,w,label,title):
        r.rect(x,y,w,61,INK,6)
        r.text(label,x+12,y+10,8,BOLD,ACCENT)
        r.text(title,x+12,y+30,12,BOLD,white)
    box(60,244,147,"STATE 0","Menu entry")
    box(344,244,177,"STATE 1","Selecting entry")
    box(344,379,177,"STATE 2","Selecting loop")
    box(60,379,147,"STATE 3","Moving loop")
    box(344,511,177,"STATE 4","Victory entry")
    r.arrow([(207,274),(342,274)]);r.text("A: choose level",235,255,8,SANS,GREEN)
    r.arrow([(432,305),(432,377)]);r.text("Load level",441,332,8,SANS,GREEN)
    r.arrow([(344,397),(209,397)]);r.text("A: move",245,381,8,SANS,GREEN)
    r.arrow([(207,425),(342,425)]);r.text("A: select",243,432,8,SANS,GREEN)
    r.arrow([(134,379),(134,307)]);r.text("B",143,338,9,BOLD,GREEN)
    r.arrow([(521,410),(540,410),(540,225),(134,225),(134,242)])
    r.text("B: return to menu",386,211,8,SANS,GREEN)
    r.arrow([(432,440),(432,509)]);r.text("Cao Cao escapes",441,476,8,SANS,GREEN)
    r.arrow([(344,542),(30,542),(30,274),(58,274)])
    r.text("A: back to menu",127,523,8,SANS,GREEN)
    y=r.heading("8", "Optimization",610)
    optim=["Prepare graphics in shadowSCRN to reduce direct VRAM work.",
           "Select a transfer routine based on the affected region's height.",
           "Expand transfer loops to reduce loop and function-call overhead.",
           "Update only the area that changed."]
    for i,s in enumerate(optim):
        r.rect(46,y+4+i*25,5,5,GREEN)
        r.text(s,62,y+i*25,10)
    r.para("<b>Edition note.</b> Sections 1-8, the configuration example and both original figures are retained in a new layout. Text is lightly edited for clarity. Labeled source notes reconcile the report with the accompanying code; no original source file or report is altered.",44,754,507,8.2,MUTED)
    r.save()
    print(OUT)


if __name__ == "__main__":
    create()
