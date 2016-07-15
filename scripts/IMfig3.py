## Copyright 2009-2016  Jody Hey
## renamed to IMfig3
## returning to this 5/11/2016  so it can handle latest output  and added some functionality

##IMfig  2/24/2012 version
##recent fixes
## fixed a problem when reading a file from a run done with a prior file
## fixed a problem reading the marginal value tables for population sizes
## added error trapping for when it is run without -d option on file without demographic info
##  trapped '#' and '#?' and '?' symbols when scanning population size values

## IMfig makes an eps file
## IMfig can be run from within a python interpreter such as IDLE,
##  or from the command line if python is installed.
## Read the documentation for details on running the program


import math
import sys

## constants that don't change (some can be adjusted in effect by multiplying by scalars given by user)
arrowheadwidthdefault = 0.01  ## arrow size
popboxspacedefault = 0.1  ## spacing between population boxes
curveheightdefault = 0.03  ## curvature of migration arrows
tfactor = 1.0  ## a fudge factor for moving things to the right of splittime arrows
min2NM = 0.005 ## the smallest value plotted by IM programs for 2NM



##***********************************************************************************
##////////////// FUNCTIONS FOR GENERATING EPS FILE   ////////////////////////////////
##***********************************************************************************

def w(s):
    "simple function to make it easier to print to the eps file without having to repeat code text "
    epsf.write(s + "\n")

def apoint(rpoint):
    """ rpoint is a list of length 2, convert a relative point to an absolute point
        x value is in position 0,  y value in position 1
        maxll is the lower left point of the plot
        maxur is the upper right point
        globalscale is an overall scalar of plot size
        localxscale is an x dimensional scalar of plot size so the x dimension can be changed without affecting the y dimension
    """
    global localxscale
    tempy = maxll[1] + globalscale*rpoint[1]*(maxur[1]-maxll[1])
    if localxscale != -1:
        tempx = maxll[0] +  localxscale*globalscale*rpoint[0]*(maxur[0]-maxll[0])
    else :
        tempx = maxll[0] + globalscale*rpoint[0]*(maxur[0]-maxll[0])
##    print tempx, maxur[0], tempx-maxur[0]
    if tempx - maxur[0] > 0 and tempx - maxur[0] < 1e-7:
        tempx = maxur[0]
    if tempx > maxur[0] :
        print "problem x value : ",tempx,   " max x allowed : ",maxur[0]
    return [tempx,tempy]

def rapoint(rpoint):
    """ relative point
        this is called from a function where the scale has been reset
    """
    return [rpoint[0]*globalscale*(maxur[0]-maxll[0]),\
            rpoint[1]*globalscale*(maxur[1]-maxll[1])]

def textwide(s, tf):
    """ approx width of text """
    w = 350 ## default ok for Arial or Helvetica
    if font == "Times-roman":
        w = 330
    if font == "Courier":
        w = 390
    if fontfixed == False:
        localfontsize = int(fontsize*globalscale)
    else:
        localfontsize = int(fontsize)
    return tf*localfontsize * len(s)*w/(1000*(maxur[0] - maxll[0]))

def dotext(rpoint,text,angle, bi):
    global font, bifont
    """ print text beginning at rpoint at angle """
##    w("/Arial findfont")
    if bi:
        w("/%s findfont" % bifont)
    else:
        w("/%s findfont" % font)
    if fontfixed == False:
        localfontsize = int(fontsize*globalscale)
    else:
        localfontsize = int(fontsize)
    w("%d scalefont" % localfontsize)
    w("setfont")
    w("newpath")
    p = apoint(rpoint)
    if angle != 0 :
        w("gsave")
        w("%d %d translate" % (p[0],p[1]))
        w("%d  rotate" % angle)
        w("0  0 moveto")
        w("(" + text + ") show")
        w("grestore")
    else :
        w("%d %d moveto" % (p[0],p[1]))
        w("(" + text + ") show")

def curvecontrol(p1,p2, u_or_d):
    """ returns two control points to draw a curve between two points
        that are the corners of a box
        u_or_d is 1 to draw the curve above the line between the two point
        or 0 to draw the curve below the line between the two points
    """
##    four possibile orders:
##      A  p1 lower and to left of p2
##      B  p1 lower and to right of p2
##      C  p1 higher and to left of p2
##      D  p1 higher and to right of p2
##    B and C are reverse of each other
##    A and D are reverse of each other
##    so only 2 types of pairs really
##    each has a curve up or curve down possibility
##    start by converting D to A,  and C to B
    e1 = 0.0001
    e2 = 0.9
    e1c = 1-e1
    e2c = 0.5
    cp1 = []
    cp2 = []
    if p2[1] < p1[1] :
        resort = True
        ptemp = p2
        p2 = p1
        p1 = ptemp
    else :
        resort = False
    if p1[0] < p2[0] :   ## type A
        if u_or_d :   ## curve up
            cp1.append( ((p2[0]-p1[0]) * e1) + p1[0])
            cp1.append( ((p2[1]-p1[1]) * e2) + p1[1])
            cp2.append( ((p2[0]-p1[0]) * e2c) + p1[0])
            cp2.append( ((p2[1]-p1[1]) * e1c) + p1[1])
        else :
            cp1.append( ((p2[0]-p1[0]) * e2) + p1[0])
            cp1.append( ((p2[1]-p1[1]) * e1) + p1[1])
            cp2.append( ((p2[0]-p1[0]) * e1c) + p1[0])
            cp2.append( ((p2[1]-p1[1]) * e2c) + p1[1])
    else :  ## type B
        if u_or_d :   ## curve up
            cp1.append( p1[0]-((p1[0]-p2[0]) * e1))
            cp1.append( ((p2[1]-p1[1]) * e2) + p1[1])
            cp2.append( p1[0] - ((p1[0]-p2[0]) * e2c))
            cp2.append( ((p2[1]-p1[1]) * e1c) + p1[1])
        else :
            cp1.append( p1[0]-((p1[0]-p2[0]) * e2))
            cp1.append( ((p2[1]-p1[1]) * e1) + p1[1])
            cp2.append( p1[0]-((p1[0]-p2[0]) * e1c))
            cp2.append( ((p2[1]-p1[1]) * e2c) + p1[1])
    if resort:
        ptemp = cp2
        cp2 = cp1
        cp1 = ptemp
    return cp1,cp2

def curvebox(cdim, cbox, width,color, graylevel,popnum,dash):
    "like box but with curved corners, size of the curve set by curvesize"
    if dash > 0 :
        w("[%d %d] 0 setdash" % (dash,dash))

    ll = cbox[0]
    ur = cbox[1]
    curvesizedefine = 0.02
    if cdim == -1:
        cdim = (maxur[0]-maxll[0]) *curvesizedefine
    lla = apoint(ll)
    ura = apoint(ur)
    if ura[0]-lla[0] < 2*cdim or  ura[1]-lla[1] < 2* cdim :
        cdim = min(ura[0]-lla[0],ura[1]-lla[1])/2.0
    ula = [lla[0],ura[1]]
    lra = [ura[0],lla[1]]
    if rgbcolor:
         w("%f %f %f setrgbcolor" % (rgbset[popnum][0],rgbset[popnum][1],rgbset[popnum][2]))
    else:
        if color != black:
            color = blue
            gcolor = []
            for i in range(3):
                if color[i] == 0:
                    gcolor.append(graylevel)
                else:
                    gcolor.append(color[i])
            w("%f %f %f setrgbcolor" % (gcolor[0],gcolor[1],gcolor[2]))
        else:
            w("%f setgray" % graylevel)
    w("newpath")
    w("%d  %d  moveto" %(lla[0]+cdim,lla[1]))

    cp1 = [lra[0]-cdim,lra[1]]
    cp2 = [lra[0],lra[1]+cdim]

    w("%d  %d  lineto" %(cp1[0],cp1[1]))

    ccpoints = curvecontrol(cp1,cp2,0)
    w("%d %d %d %d %d  %d  curveto" %(ccpoints[0][0],ccpoints[0][1],ccpoints[1][0],ccpoints[1][1],cp2[0],cp2[1]))

    cp1=[ura[0],ura[1]-cdim]
    cp2 = [ura[0]-cdim,ura[1]]

    w("%d  %d  lineto" %(cp1[0],cp1[1]))
    ccpoints = curvecontrol(cp1,cp2,1)
    w("%d %d %d %d %d  %d  curveto" %(ccpoints[0][0],ccpoints[0][1],ccpoints[1][0],ccpoints[1][1],cp2[0],cp2[1]))

    cp1 = [ula[0]+cdim,ula[1]]
    cp2 = [ula[0],ula[1]-cdim]

    w("%d  %d  lineto" %(cp1[0],cp1[1]))
    ccpoints = curvecontrol(cp1,cp2,1)
    w("%d %d %d %d %d  %d  curveto" %(ccpoints[0][0],ccpoints[0][1],ccpoints[1][0],ccpoints[1][1],cp2[0],cp2[1]))

    cp1 = [lla[0],lla[1]+cdim]
    cp2 = [lla[0]+cdim,lla[1]]

    w("%d  %d  lineto" %(cp1[0],cp1[1]))
    ccpoints = curvecontrol(cp1,cp2,0)
    w("%d %d %d %d %d  %d  curveto" %(ccpoints[0][0],ccpoints[0][1],ccpoints[1][0],ccpoints[1][1],cp2[0],cp2[1]))

    w("closepath")
    width = float(width)
    w("%f setlinewidth" % (width*globalscale))
    w("stroke")
    if simplecolor or rgbcolor:
        w("0 0 0  setrgbcolor")
    else:
        w("0 setgray")
    if dash > 0 :
        w("[] 0 setdash")

    return cdim

## not used as of 7/16/09
def rectangularbox(ll,ur):
    """draw a box from relative lower left to relative upper right
    max of values is 1"""
    lla = apoint(ll)
    ura = apoint(ur)
    ula = [lla[0],ura[1]]
    lra = [ura[0],lla[1]]
    w("newpath")
    w("%d  %d  moveto" %(lla[0],lla[1]))
    w("%d  %d  lineto" %(lra[0],lra[1]))
    w("%d  %d  lineto" %(ura[0],ura[1]))
    w("%d  %d  lineto" %(ula[0],ula[1]))
    w("%d  %d  lineto" %(lla[0],lla[1]))

    w("closepath")
    w("%f setlinewidth", (2.0 * globalscale))
    w("stroke")

def aline(p, width, dash, graylevel):
    """ p is a list of points in relative space (0-1)
        dash is the spacing (in point scale) of dashes in the line
        if dash is zero there is no dashing """
    if graylevel > 0 :
        w("%f setgray" %graylevel)
    ap = []
    for i in range(len(p)) :
        ap.append(apoint(p[i]))
    if dash > 0 :
        w("[%d %d] 0 setdash" % (dash,dash))

    w("%d %d moveto" % (ap[0][0],ap[0][1]))
    for j in range(1,len(p)):
        w("%d %d lineto" % (ap[j][0],ap[j][1]))
    width*= globalscale
    w("%f setlinewidth" % width)
    w("stroke")
    w("[ ] 0 setdash")
    if graylevel > 0 :
        w("0 setgray")

def arrowheada(head,headwidth,angle, color) :
    """ draw arrowhead width on the same scale as points in head
    head is the center of the arrowhead
    angle = 0 has the arrow pointing to the right """

    holdhead = apoint(head)
    head = [0,0]
    tip = rapoint([head[0] + headwidth,head[1]])
    p1 = rapoint([head[0] - headwidth,head[1] + headwidth])
    p2 = rapoint([head[0] - headwidth,head[1] - headwidth])
    c1 = rapoint([head[0],head[1]-headwidth/2])
    c2 = rapoint([head[0],head[1]+headwidth/2])
    w("gsave")
    w("%d %d translate" % (holdhead[0],holdhead[1]))
    w("%d  rotate" % angle)
    w("%d %d moveto" % (p1[0],p1[1]))
    w("%d %d lineto" % (tip[0],tip[1]))
    w("%d %d lineto" % (p2[0],p2[1]))
    w("%d %d %d %d %d %d curveto"% (c1[0],c1[1],c2[0],c2[1],p1[0],p1[1]))
    w("closepath")
    w("fill")
    w("grestore")

def arrowa(head,tail,direc, color, graylevel) :
    """ draw an arrow. head and tail are points, width is on the same scale
    direc = 0 right, 1 up, 2 left, 3 down"""
    headwidth = arrowheadwidthdefault*arrowheightadj
    if (direc == 0):
        headadj = [head[0]-headwidth,head[1]]
    if (direc == 1):
        headadj = [head[0],head[1]-headwidth]
    if (direc == 2):
        headadj = [head[0]+headwidth,head[1]]
    if (direc == 3):
        headadj = [head[0],head[1]+headwidth]
    if color != black:
        color = blue
        gcolor = []
        for i in range(3):
            if color[i] == 0:
                gcolor.append(graylevel)
            else:
                gcolor.append(color[i])
        w("%f %f %f setrgbcolor" % (gcolor[0],gcolor[1],gcolor[2]))
    else:
        w("%f setgray" % graylevel)
    arrowheada(headadj,headwidth,direc*90, black)
    ahead = apoint(headadj)
    atail = apoint(tail)
    w("%d %d moveto" % (ahead[0],ahead[1]))
    w("%d %d lineto" % (atail[0],atail[1]))
    w("%f setlinewidth" % (2*globalscale))
    w("stroke")
    if simplecolor or rgbcolor:
        w("0 0 0  setrgbcolor")
    else:
        w("0 setgray")

## curvearrow not used as of 7/15/09
def curvearrow(head,tail,curveheight,headwidth,direc, width, dash) :
    """ direct can be 0 or 2 (right or left)  if 0 curveheight is positive and curve goes up from
        the tail and then down to the head
        if direc is 2  then curve is interpreted to be negative and curve goes down from the tail
        and then up to the head """
    if (direc == 0):
        headadj = [head[0]-headwidth,head[1]]
        arrowheada(headadj,headwidth,340, black)        ## head tilted down to the right
        cp1 = [tail[0] + (headadj[0] - tail[0])*0.8,headadj[1] + curveheight]
        cp2 = [tail[0] + (headadj[0] - tail[0])*0.2,headadj[1] + curveheight]
    if (direc == 2):
        headadj = [head[0]+headwidth,head[1]]
        arrowheada(headadj,headwidth,160, black)       ## head tilted up to the left
        cp1 = [headadj[0] + (tail[0] - headadj[0])*0.2,headadj[1] - curveheight]
        cp2 = [headadj[0] + (tail[0] - headadj[0])*0.8,headadj[1] - curveheight]
    ahead = apoint(headadj)
    atail = apoint(tail)
    acp1 = apoint(cp1)
    acp2 = apoint(cp2)
    w("%f setlinewidth" % (width*globalscale))
    if dash > 0 :
        w("[%d %d] 0 setdash" % (dash,dash))
    w("%d %d moveto" % (ahead[0],ahead[1]))
    w("%d %d  %d  %d  %d  %d curveto" % (acp1[0],acp1[1],acp2[0],acp2[1],atail[0],atail[1]))
    w("stroke")
    w("[ ] 0 setdash")


def migrationcurvearrow(val2NM,head,tail,direc, color) :
    """ direct can be 0 or 2 (right or left)  if 0 curveheight is positive and curve goes up from
        the tail and then down to the head
        if direc is 2  then curve is interpreted to be negative and curve goes down from the tail
        and then up to the head """

    curveheight = curveheightdefault
    c2height = arrowheadwidthdefault
    headwidth = c2height*1.5*arrowheightadj
    width = 1.5
    width = 2.5
    if (direc == 0): ## arrow to the right,  line is shifted up, text is below line
        textpoint=[tail[0],tail[1]-curveheight]
        cheadadj = [head[0]-headwidth,head[1]+c2height]
        ctail =  [tail[0],tail[1]+c2height]
        arrowheadpoint = [cheadadj[0], head[1] + c2height/1.2]
        if simplecolor or rgbcolor:
            w("%f %f %f setrgbcolor" % (color[0],color[1],color[2]))
        arrowheada(arrowheadpoint,headwidth,330, color)        ## head tilted down to the right
        if simplecolor or rgbcolor:
            w("0 0 0 setrgbcolor")
        if abs(cheadadj[0] - ctail[0]) > 0:
            curveheightmultiplier =math.pow(abs(cheadadj[0] - ctail[0])/0.15,0.1)
        else:
            curveheightmultiplier = 1
        cp1 = [ctail[0] + (cheadadj[0] - ctail[0])*0.8,cheadadj[1] + curveheight*curveheightmultiplier]
        cp2 = [ctail[0] + (cheadadj[0] - ctail[0])*0.2,cheadadj[1] + curveheight*curveheightmultiplier]
        textpoint = [cp2[0],cheadadj[1]-curveheight/3]
    if (direc == 2): ## arrow to the left, line is shifted down, text is above line
        cheadadj = [head[0]+headwidth,head[1]]
        textpoint = [cheadadj[0]+c2height,cheadadj[1]]
        ctail = tail
        arrowheadpoint = [cheadadj[0], cheadadj[1] + c2height/3.5]
        if simplecolor or rgbcolor:
            w("%f %f %f setrgbcolor" % (color[0],color[1],color[2]))
        arrowheada(arrowheadpoint,headwidth,150,color)       ## head tilted up to the left
        if simplecolor or rgbcolor:
            w("0 0 0 setrgbcolor")
        if abs(cheadadj[0] - ctail[0]) > 0:
            curveheightmultiplier = math.pow(abs(cheadadj[0] - ctail[0])/0.15,0.1)
        else:
            curveheightmultiplier = 1

        cp1 = [cheadadj[0] + (ctail[0] - cheadadj[0])*0.2,cheadadj[1] - curveheight*curveheightmultiplier]
        cp2 = [cheadadj[0] + (ctail[0] - cheadadj[0])*0.8,cheadadj[1] - curveheight*curveheightmultiplier]
        textpoint = [cp1[0],cheadadj[1]-curveheight/3]

    ahead = apoint(cheadadj)
    atail = apoint(ctail)
    acp1 = apoint(cp1)
    acp2 = apoint(cp2)
    if width > 0 :
        if simplecolor or rgbcolor:
            w("%f %f %f setrgbcolor" % (color[0],color[1],color[2]))
        w("%f setlinewidth" % (width*globalscale))
        w("%d %d moveto" % (ahead[0],ahead[1]))
        w("%d %d  %d  %d  %d  %d curveto" % (acp1[0],acp1[1],acp2[0],acp2[1],atail[0],atail[1]))
        w("stroke")


        if simplecolor or rgbcolor:
            w("%f %f %f setrgbcolor" % (255,255,255))#0,0,0))
        w("%f setlinewidth" % 0.5)
        w("%d %d moveto" % (ahead[0],ahead[1]))
        w("%d %d  %d  %d  %d  %d curveto" % (acp1[0],acp1[1],acp2[0],acp2[1],atail[0],atail[1]))
        w("stroke")
        if simplecolor or rgbcolor:
            w("0 0 0 setrgbcolor")
        dotext(textpoint,val2NM,0, True)
        if simplecolor or rgbcolor:
            w("0 0 0 setrgbcolor")


##***********************************************************************************
##////////////// FUNCTIONS FOR GETTING VALUES OUT OF INPUT FILE        //////////////
##***********************************************************************************
##    These functions put information in slist, a 2D global list of lists array
##    The main function here readimfile() which builds slist[][]
##    Each list in slist contains the details regarding a particular type of info to be
##    obtained from the input file
##    slist[i][0] - a brief text description about the category of information
##    slist[i][1] - a boolean value that is initialized as False, but becomes True after the info is obtained
##    slist[i][2] - the name of the function that reads the information of that type
##    slist[i][3] - the string used to search the input file,  when it is found the function is called
##    slist[i][ > 3 ] - the actual information, the types and number of values vary depending on the category of information
##      all of the functions (names in slist[i][2] are called with
##            slist[i][2](imfile,imfileline,slist[i][3],numpops)
##        what the function returns is appended to slist[i]

def get_input_file_name (f,a,s,numpops) :
    return a[len(s):len(a)].strip()

def check_ghost_status(f,a,s,numpops):
    global useghost
    useghost =  (a.find("-j") >= 0) and ( "4" in  a[a.find("-j")+1:])  ## should only be true if -j is there with a 4


def get_population_names (f,a,s,numpops) :
    aa = f.readline().strip()
    plist = []
    i = 0
    while aa.find("Population") >= 0 :
        plist.append(aa[aa.find(":")+1:len(aa)].strip())
        ## reset names for chimpanzee paper, these lines not relevant otherwise
        if plist[i] == "paniscus":
            plist[i] = "bonobo"
        if plist[i] == "schweinfurthii":
            plist[i] = "eastern"
        if plist[i] == "troglodytes":
            plist[i] = "central"
        if plist[i] == "verus":
            plist[i] = "western"
        i += 1
        aa = f.readline().strip()
    if useghost:
        plist.append("ghost")
    return plist

def get_population_tree (f,a,s,numpops) :
    if useghost:  # read the next line
        aa = f.readline().strip()
        return  aa.split()[-1]
    return a[len(s):len(a)].strip()

def get_popsize_param (f,a,s,numpops) :
    """ read the table of marginal distributions for population sizes:
    For each population it reads:
    the label of the parameter
    the HiSmth value
    the HPD95Lo value
    the HPD95Hi value """
    psp = []
    for i in range(4) :
        aa = f.readline().split()
    for i in range(2*numpops - 1):
        psp.append([])
        psp[i].append(aa[i+1])
    aa = f.readline().split()
    while len(aa) > 0:
        while aa.count("#"):
            aa.remove("#")
        while aa.count("#?"):
            aa.remove("#?")
        while aa.count("?"):
            aa.remove("?")
        found = False
        if aa[0]=="HiPt" or aa[0]=="HPD95Lo"  or aa[0]=="HPD95Hi" : found = True
        if found :
            for i in range(2*numpops - 1):
                psp[i].append(float(aa[i+1].strip('?#')))
        aa = f.readline().split()
    return psp

def get_t_param (f,a,s,numpops) :
    """ read the table of marginal distributions for splitting times:
        For each splittingtime it reads:
            the label of the parameter
            the HiSmth value
            the HPD95Lo value
            the HPD95Hi value """
    psp = []
    aa = f.readline().split()
    while aa[0] != "Value" :
        aa = f.readline().split()
    for i in range(numpops-1):
        psp.append([])
        psp[i].append(aa[i+1])
    aa = f.readline().split()
    while len(aa)> 0:
        while aa.count("?"):
            aa.remove("?")
        while aa.count("#"):
            aa.remove("#")
        found = False
        if aa[0]=="HiSmth" or aa[0]=="HPD95Lo"  or aa[0]=="HPD95Hi" : found = True
        if found :
            for i in range(numpops-1):
                psp[i].append(float(aa[i+1].strip('?#')))
        aa = f.readline().split()
    return psp

##def get_2NM (f,a,s,numpops) :
##    """ record the estimate of 2NM as well as the probability at 2NM = 0 and the probability at the peak
##        returns a list of lists, one for each 2NM value, the elemenst are:
##            the name,  e.g. 2N0m0>1
##            the estimated 2NM value
##            the posterior probability at 2NM = 0
##            the highest posterior probability
##    """
##    psp = []
##    aa = f.readline().split()
##    while aa[0] != "Value" :
##        aa = f.readline().split()
##    nummigp = len(aa)-1
##
##    for i in range(1,len(aa)):
##        psp.append([])
##        psp[i-1].append(aa[i])
##    s = f.readline()
##    while s.find("HiSmth") < 0 :
##        s = f.readline()
##    aa = s.split()
##    for i in range(1,1+nummigp):
##        psp[i-1].append(float(aa[i]))
##    s = f.readline()
##    while len(s)<2 or s.split()[0] != "0" :
##        s = f.readline()
##        if s.find("HiPt") > 0 :
##            holds = s
##    aa = s.split()
##    for i in range(nummigp):
##        pos = 2*(i +1)
##        psp[i].append(float(aa[pos]))
##    aa = holds.split()
##    for i in range(nummigp):
##        pos = 2*(i +1)
##        psp[i].append(float(aa[pos]))
##    return psp

## get_2NM_alt() differs from get_2NM.  It uses the
## table on Marginal Peak Locations and PRobabilities, rather thatn the histograms
##  using this requires a change in readimfile() to make sure this gets called
##  and a change in print_mcurves(),  llr does not need to be calculated using
##  get_2NM_alt()
##  The reason for using get_2NM_alt() is that it calculates the LLR stat more precisely
## and is more likely to get statistical significance (less conservative)

def get_2NM_alt (f,a,s,numpops) :
    """ use the table on Marginal Peak Locations and PRobabilities, rather thatn the histograms
        Record the estimate of 2NM as well as the probability at 2NM = 0 and the probability at the peak
        returns a list of lists, one for each 2NM value, the elemenst are:
            the name,  e.g. 2N0m0>1
            the estimated 2NM value
            the likelihood ratio test value
    """
    psp = []
    nummigp = 0
    while True :
        newn = 0
        aa = f.readline().split()
        for i in range(1,len(aa),2):
            psp.append([])
            psp[newn + nummigp].append(aa[i])
            newn += 1
        for i in range (3):
            s = f.readline()
        aa = s.split()
        ii = 0
        for i in range(1,len(aa),2):
            psp[nummigp + ii].append(float(aa[i]))
            ii += 1
        s = f.readline()
        aa = s.split()
        newaa = []
        for i in aa:
            if i=="bad":
                newaa.append("0.0ns")  ## if a 2NM test returns "bad value"  make it as if it was not significant
            else:
                if i != "value":
                    newaa.append(i)
        aa = newaa
        ii = 0
        for i in range(1,len(aa)):
            temp = aa[i]
            while temp[len(temp)-1] == "s" or temp[len(temp)-1] == "n" or temp[len(temp)-1] == "*":
                temp = temp[0:len(temp)-1]
            psp[nummigp + ii].append(float(temp))
            ii += 1
        s = f.readline()
        while s.upper().find("Population Migration (2NM) Terms".upper()) ==-1 and s.upper().find("HISTOGRAMS")==-1:
            s = f.readline()
        if s.upper().find("HISTOGRAMS")>= 0:
            break;
        nummigp += newn
    return psp

def get_demog_scales (f,a,s,numpops) :

    psp = [0,0,0]
    for i in range(10): ## go down several lines and look for the necessary information,  very crude and
        aa = f.readline().split()
        if aa[0]=="Generation" and aa[1]=="time" :
            psp[0] = float(aa[len(aa)-1])
        if aa[0]=="Geometric" and aa[3]=="mutation" :
            psp[1] = float(aa[len(aa)-1])
        if aa[0]=="Geometric" and aa[3]=="ML" :
            psp[2] = float(aa[len(aa)-1])
    return psp

def get_parameter_priors (f,a,s,numpops) :
    psp = [["population size","uniform"],["migration","uniform"],["splittime","uniform"]]
    aa = f.readline()
    for i in range(3):
        aa = f.readline().split()
        psp[i].append(float(aa[len(aa)-1]))
        if aa.count("exponential") > 0 :
            psp[i][1] = "exponential"
    return psp


## localscale is 1 if (maxur[0]-maxll[0]) corresponds to Ne of 1e6
def calc_scaledvals(slist):
    global numpops
    gentime= slist[7][4][0]
    timeumean = slist[7][4][1]
    scaleumean = slist[7][4][2]
    scaledpop = []
    for i in range(2*numpops-1):
        scaledpop.append(slist[4][4][i][1]/(4.0 * timeumean*gentime))
    scaledtime = []
    for i in range(numpops-1):
        scaledtime.append(slist[5][4][i][1] * (scaleumean/timeumean))
    return scaledpop, scaledtime


def readimfile(imfilename) :
    imfile = file(imfilename)
    global slist
    global numpops
    global useghost
    numpops = 0
    useghost = False
    slist = [["ghost status",False,check_ghost_status,"Model options on command line"],\
             ["inputfile",False,get_input_file_name,"Text from input file:"],\
             ["pop names",False,get_population_names,"- Population Names -"],\
             ["pop tree",False,get_population_tree,"Population Tree :"],\
             ["population size parameter info",False,get_popsize_param,"MARGINAL DISTRIBUTION VALUES AND HISTOGRAMS OF POPULATION SIZE AND MIGRATION PARAMETERS"],\
             ["splitting time parameter info",False,get_t_param,"MARGINAL DISTRIBUTION VALUES AND HISTOGRAMS OF PARAMETERS IN MCMC"],\
##             ["migration parameter info",False,get_2NM,"POPULATION MIGRATION (2NM) POSTERIOR PROBABILITY HISTOGRAMS"],\
             ["migration parameter info",False,get_2NM_alt,"Population Migration (2NM) Terms"],\
             ["demographic scales",skipdemographicscaling,get_demog_scales,"MARGINAL DISTRIBUTION VALUES IN DEMOGRAPHIC UNITS"] #,\
##             ["parameter priors",False,get_parameter_priors,"Parameter Priors"] \  ignore this I think
             ]
    ##  slist[7][1] = skipdemographicscaling ## if true skip the demographic scales
    imfileline  = imfile.readline()
    while imfileline != '':
        checkdone = True
        for i in range(len(slist)):
            checkdone =  checkdone and slist[i][1]

            if slist[i][1] == False and imfileline.upper().find(slist[i][3].upper()) >= 0 :
                if slist[i][0] == "ghost status" :
                    slist[i][2](imfile,imfileline,slist[i][3],numpops)
                else:
                    slist[i].append(slist[i][2](imfile,imfileline,slist[i][3],numpops))
                slist[i][1] = True
                if slist[i][0] == "pop names" :
                    numpops = len(slist[i][4])
##                print slist[i][0]
        if checkdone :
            break
        imfileline  = imfile.readline()
    imfile.close()
    (scaledpop,scaledtime) = ([],[])
    if skipdemographicscaling:
        slist[7][1] = False
    else:
        if len(slist[7]) == 4:
            print  "**IMfig error - Information in demographic units not found, use -d option"
            quit()
        if len(slist[7][4])==3:
            (scaledpop, scaledtime) = calc_scaledvals(slist)
    return numpops, slist, scaledpop, scaledtime

##***********************************************************************************
##////////////// FUNCTIONS FOR READING THE POPULATION TREE STRING  //////////////////
##***********************************************************************************
def parenth(tempcurrent,numpops,poptree,poptreestring,stringspot,ancestralpopnums,rootpop,nextnode,periodi):
    current = ancestralpopnums[tempcurrent]
##    print "current : ", current, " nextnode : ", nextnode
    stringspot += 1
    while poptreestring[stringspot].isspace():
        stringspot += 1
    while True :
        if poptreestring[stringspot].isdigit():
            if stringspot <= len(poptreestring)-2 and poptreestring[stringspot+1].isdigit() :
                ts = poptreestring[stringspot] + poptreestring[stringspot+1]
                itemp = int(ts)
            else:
                itemp = int(poptreestring[stringspot])
            stringspot += 1
            if  poptree[current][2] == -1 :
                poptree[current][2] = itemp
            else:
                poptree[current][3] = itemp
            poptree[itemp][4] = current
        if poptreestring[stringspot] == ',' :
            stringspot += 1
        if poptreestring[stringspot] == '(' :
            if nextnode == -1:
                nextnode = numpops + 1
            else:
                nextnode += 1
            poptree[ancestralpopnums[nextnode]][4] = current
            if  poptree[current][2] == -1 :
                poptree[current][2] =   ancestralpopnums[nextnode]
            else:
                poptree[current][3] =   ancestralpopnums[nextnode]
            (poptree,rootpop,stringspot,periodi,nextnode) = parenth(nextnode,numpops,poptree,poptreestring,stringspot,ancestralpopnums,rootpop,nextnode,periodi)
        if poptreestring[stringspot] == ')' :
            break
    stringspot += 1
    if poptreestring[stringspot] == ':' :
        stringspot += 1
        if stringspot <= len(poptreestring)-2 and poptreestring[stringspot+1].isdigit() :
            ts = poptreestring[stringspot] + poptreestring[stringspot+1]
            i = int(ts)
        else:
            i = int(poptreestring[stringspot])
        if i < numpops :
            print " wrong number of ancestral populations indicated. string %c " % poptreestring[stringspot]
        periodi = i- numpops
        poptree[current][0] = periodi + 1
        poptree[poptree[current][2]][1] = periodi + 1
        poptree[poptree[current][3]][1] = periodi + 1
        if i >= 10 :
            stringspot += 2
        else:
            stringspot += 1
    else:
        poptree[current][0] = periodi + 1
        poptree[poptree[current][2]][1] = periodi + 1
        poptree[poptree[current][3]][1] = periodi + 1
        periodi += 1
    if poptree[current][4] != -1 :
        current = poptree[current][4]
    else :
        periodi += 1
        poptree[current][1] = -1
        rootpop = current

    return poptree,rootpop,stringspot,periodi,nextnode

def parenth0(current,poptree,poptreestring,stringspot,ancestralpopnums):
    nextlistspot = 0
    ne = stringspot
    popennum = 0
    psetlist = []
    for i in range(current):
        psetlist.append(-1)
    while ne < len(poptreestring) :
        if poptreestring[ne]=='(':
            psetlist[nextlistspot] = popennum
            nextlistspot += 1
            popennum += 1
            ne += 1
        else :
            if poptreestring[ne]==')':
                ne += 2
                if ne <= len(poptreestring)-2 and poptreestring[ne+1].isdigit() :
                    ts = poptreestring[ne] + poptreestring[ne+1]
                    itemp = int(ts)
                else:
                    itemp = int(poptreestring[ne])
                ancestralpopnums[current + psetlist[nextlistspot - 1]] = itemp
                nextlistspot -= 1
            else:
                ne += 1
    return poptree, ancestralpopnums

def set0 (strlist,pos):
    """ removes elements of a list from pos to the end, save these as a separate list """
    hold = []
    while len(strlist) > pos:
        hold.append(strlist.pop(len(strlist)-1))
    hold.reverse()
    return strlist,hold

def strlistadd(strlist,pos,c):
    if pos > (len(strlist)-1) :
        strlist.append(c)
    else:
        strlist[pos] = c
    return strlist

def joinlist(list1, list2) :
    for i in range(len(list2)):
        list1.append(list2[i])
    return list1


def rewrite (substr, numpops) :
    """    rewrite() rewrites the treestring in a standard order
        swivels nodes,  if both have node sequence values, the one with the lower node sequence value (periodi[]) goes on the left
        if only one has a node sequence value,  it goes on the right
            when neither has a node sequence value, the one with the lowest node number go on the left
       uses simple sorting for a pair.  To handle multifurcations, must put in proper sorting
       based on code in imamp  3_9_09
       works recursively  """

    slengths = [0]* (2*numpops-1)
    firstint = [0] * (2*numpops - 1)
    holdsubs = [[]] * (2*numpops - 1)
    periodi = [0] * (2*numpops - 1)
    pos = 1
    subpos = pos
    subcount = 0
    pcount = 0
    slengths[subcount] = 0
    while 1 :
        if substr[pos] == '(' :
            pcount += 1
        if substr[pos] == ')' :
            pcount-= 1
        pos+= 1
        slengths[subcount]+= 1
        if (pcount == 0):
            if (slengths[subcount] > 1) :
                pos+= 1
                i = int(substr[pos])
                if pos <= len(substr)-2 and substr[pos+1].isdigit() :
                    ts = substr[pos] + substr[pos+1]
                    i = int(ts)
                else:
                    i = int(substr[pos])
                periodi[subcount] = i
                if (i >= 10) :
                    pos += 2
                    slengths[subcount] += 3
                else :
                    pos+= 1
                    slengths[subcount] += 2
            else :
                periodi[subcount] = -1
            holdsubs[subcount] = substr[subpos:pos]
            (holdsubs[subcount],hold) = set0(holdsubs[subcount],slengths[subcount])
            i = 0
            while (holdsubs[subcount][i].isdigit() == False):
                i+= 1
            firstint[subcount] = int(holdsubs[subcount][i])
            subcount+= 1
            slengths[subcount] = 0
            if (substr[pos] == ','):
                pos+= 1
            subpos = pos
        if pos >= len(substr) :
            break
    if ((periodi[0] > periodi[1] and periodi[0] >= 0 and periodi[1] >= 0) or (periodi[0] >= 0 and periodi[1] < 0)) :
        substr = strlistadd(substr,0,'(')
        j = slengths[1]
        k = 0
        i = 1
        while i<= j :
            substr = strlistadd(substr,i,holdsubs[1][k])
            k += 1
            i += 1
        subpos = 1
        if (slengths[1] > 2):
            (substr,hold) = set0(substr,i)
            substr[subpos:len(substr)] = rewrite (substr[subpos:len(substr)],numpops)
            substr = joinlist(substr,hold)
        substr = strlistadd(substr,i,',')
        i+= 1
        subpos = i
        j += 1 + slengths[0]
        k = 0
        while i <= j :
            substr = strlistadd(substr,i,holdsubs[0][k])
            i += 1
            k += 1
        if (slengths[0] > 2):
            (substr,hold) = set0(substr,i)
            substr[subpos:len(substr)] = rewrite (substr[subpos:len(substr)],numpops)
            substr = joinlist(substr,hold)
        substr = strlistadd(substr,i,')')
    else:
        if (firstint[0] > firstint[1] and periodi[0] < 0 and periodi[1] < 0) :
            substr = strlistadd(substr,0,'(')
            j = slengths[1]
            k = 0
            i = 1
            while  i<= j:
                substr = strlistadd(substr,i,holdsubs[1][k])
                k += 1
                i += 1
            subpos = 1
            if (slengths[1] > 2) :
                substr[subpos:len(substr)] = rewrite (substr[subpos:len(substr)],numpops)
            substr = strlistadd(substr,i,',')
            i+= 1
            subpos = i
            j += 1 + slengths[0]
            k = 0
            while i <= j :
                substr = strlistadd(substr,i,holdsubs[0][k])
                i+= 1
                k+= 1
            if (slengths[0] > 2):
                substr[subpos:len(substr)] = rewrite (substr[subpos:len(substr)],numpops)
            substr = strlistadd(substr,i,')')
        else :
            substr = strlistadd(substr,0,'(')
            subpos = 1
            if (slengths[0] > 2):
                (substr,hold) = set0(substr,slengths[0] + 1)
                substr[subpos:len(substr)] = rewrite (substr[subpos:len(substr)],numpops)
                substr = joinlist(substr,hold)
            substr = strlistadd(substr,slengths[0] + 1,',')
            subpos = slengths[0] + 2
            if (slengths[1] > 2):
                (substr,hold) = set0(substr,slengths[0] + slengths[1] + 2)
                substr[subpos:len(substr)] = rewrite (substr[subpos:len(substr)],numpops)
                substr = joinlist(substr,hold)
            substr = strlistadd(substr,slengths[0] + slengths[1] + 2,')')
    return substr


def plistbyperiod(poptreestring,numpops,poptree):
    """ generate a list, for each period this a list of the populations in that period,
         by their number from left to right"""
    plist = [[]]
    for i in range(1,len(poptreestring)):
        if poptreestring[i-1] != ":" and poptreestring[i].isdigit() :
            plist[0].append(int(poptreestring[i]))
    droppops = [[-1,-1]]
    addpop = [-1]
    numtreepops = 2*numpops - 1
    for pi in range(1,numpops):
        droppops.append([])
        k=0
        for j in range(numtreepops):
            if poptree[j][1] == pi :
                droppops[pi].append(j)
                k += 1
                if k > 2 :
                    print "droppop problem "
                    break
            if poptree[j][0] == pi :
                addpop.append(j)
        tplist1 = plist[pi-1]
        tplist2 = []
        added = False
        j = 0
        while j < len(tplist1):
            if tplist1[j] == droppops[pi][0] or tplist1[j] == droppops[pi][1] :
                if added == False :
                    added = True
                    tplist2.append(addpop[pi])
            else:
                tplist2.append(tplist1[j])
            j += 1
        plist.append(tplist2)
    return plist,droppops,addpop

def poptreeread (poptreestring,numpops) :
    """ copy of the function in imamp
         use a list of lists to hld poptree
         poptree[i] is the info for population [i]
        poptree[i][0] is the period the population begins in
         poptree[i][1] is the period it ends in
         poptree[i][2] is the left up pop
         poptree[i][3] is the right up pop
         poptree[i][4] is the downpop
         examples
        (poptree,rootpop,poptreestring,plist, droppops,addpop) = poptreeread("(((5,6):12,7):13,(4,((3,1):9,(2,0):8):10):11):14",8)
        (poptree,rootpop,poptreestring,plist) = poptreeread("(4,((3,1):6,(2,0):5):7):8",5)
         """

    poptree = []
    for i in range(numpops):
        poptree.append([-1,-1,-1,-1,-1])
        poptree[i][0] = 0
    numtreepops = 2*numpops - 1
    for i in range(numpops, numtreepops):
        poptree.append([-1,-1,-1,-1,-1])
    poptreelist = []
    for i in range(len(poptreestring)):
        poptreelist.append(poptreestring[i])
    poptreelist = rewrite(poptreelist,numpops)
    newpoptreestring = ''
    for i in range(len(poptreelist)):
        newpoptreestring += poptreelist[i]
    stringspot = 0
    ancestralpopnums = []
    for i in range(2*numpops - 1):
        ancestralpopnums.append(0)
    (poptree, ancestralpopnums) = parenth0(numpops,poptree,newpoptreestring,stringspot,ancestralpopnums)
    (poptree,rootpop,stringspot,periodi,nextnode) = parenth(numpops,numpops,poptree,newpoptreestring,stringspot,ancestralpopnums,-1,-1,0)
    (plist, droppops,addpop) = plistbyperiod(newpoptreestring,numpops,poptree)
    return poptree, rootpop, newpoptreestring, plist, droppops,addpop


def tliney(line0y, lastty, tlowest, t):
    """ returns the height in relative terms of a time t
        noticed on 5/11/2016 that this does not appear to be used
    """
    ty = t * (line0y - lastty)/tlowest + lastty
    return ty

def yline(y,farright, width, dash, graylevel) :
    """ draw a line at a specific height in relative terms """
    aline([[0,y],[farright,y]],width, dash, graylevel)

def centerbox(pop,leftpoint,poptree,popxvals) :
    """centerbox is a recursive function to find locations of population boxes
    pop is the population for which we are finding the left and right sides of the box
    centerbox returns:
        width - the difference between right and left side of population it was called with
        center - the center of the population it was called with
        new value of popxvals
            popxvals are the values to be set,  they start out with values of 0 and box width

        leftpoint
            leftpoint is the point less than which we cannot find values because a box can't be drawn there
            leftpoint is partly determined by the descendant population and partly by the population

    Start at the bottom, go up the left side then the right, recursively
    take the width of the left side and the width of the right side,
    put a spacer between, add them, and find the center
    the width and center gets returned to the basal population"""

    if poptree[pop][2] == -1 :  ## terminal population
        return popxvals[pop][1]-popxvals[pop][0],leftpoint + (popxvals[pop][1]-popxvals[pop][0])/ 2.0,popxvals, leftpoint
    else :
        ## deciding on how best to space boxes is tricky
        popspacer = popboxspaceadj * popboxspacedefault
        holdleft = leftpoint
        popxvals[poptree[pop][2]][0] = leftpoint
        popxvals[poptree[pop][2]][1] +=  leftpoint
        (lw,lc, popxvals, leftpoint) = centerbox(poptree[pop][2],leftpoint, poptree,popxvals)

        leftpoint = leftpoint + lw + popspacer
        popxvals[poptree[pop][3]][0] +=  leftpoint
        popxvals[poptree[pop][3]][1] +=  leftpoint
        (rw,rc, popxvals, leftpoint) = centerbox(poptree[pop][3],leftpoint, poptree,popxvals)
        leftpoint = holdleft
        l = max(leftpoint,\
                lc + lw/2.0 + popspacer/2.0 - (popxvals[pop][1]-popxvals[pop][0])/2.0)

        r = l + (popxvals[pop][1]-popxvals[pop][0])
        popxvals[pop][0] =l
        popxvals[pop][1]= r
        leftpoint = l
        return popxvals[pop][1]-popxvals[pop][0],leftpoint + (popxvals[pop][1]-popxvals[pop][0])/ 2.0,popxvals, leftpoint

def fround(val):
    """ does rounding """
    lval = math.log10(val)
    if lval < 0:
        lval -= 1
    rval = -int(lval) + 1
    if lval > 3:
        return str(int(round(val, rval)))
    return str(round(val, rval))

def popadjustx(popxvals):
    minx = popxvals[0][0]
    for i in range(1,len(popxvals)):
        if minx > popxvals[i][0]:
            minx = popxvals[i][0]
    for i in range(len(popxvals)):
        popxvals[i][0] -= (minx - minx_popbox)
        popxvals[i][1] -= (minx - minx_popbox)
    return popxvals

def setpopbox(ty,slist,numpops):
    """popbox[i][0] is the lowerleft point of the box
        popbox[i][0][0] contains the xdimension for the left side of the box
        popbox[i][0][1] contains the y dimension for the bottom of the box
    popbox[i][1] is the upper right
        popbox[i][1][0] contains the xdimension for the right side of the box
        popbox[i][1][1] contains the y dimension for the top of the box"""

    popxvals = []
## if scaledpop == [] then no text is written on time split line and there is more width to work with
    for i in range(2*numpops - 1):
## left side temporarily at zero, right side temporarily at upper confidence interval
        popxvals.append( [0,slist[4][4][i][1]])
    (width,c,popxvals, leftpoint) = centerbox(rootpop,0,poptree,popxvals)
    popxvals = popadjustx(popxvals)
    popbox = []

    maxwide = 0
    for i in range(2*numpops-1):
        if maxwide < (popxvals[i][1] + (slist[4][4][i][3]-slist[4][4][i][1])):
            maxwide = (popxvals[i][1] + (slist[4][4][i][3]-slist[4][4][i][1]))
    maxwide = maxwide/(1.0-minx_popbox)

    if localxscale > 0:
        maxwide *= localxscale

    farright = 0
    confint = []
    for i in range(2*numpops-1):
        confint.append([])
        confint[i].append(minx_popbox + ((popxvals[i][1] - (slist[4][4][i][1]-slist[4][4][i][2]))/maxwide))
        confint[i].append(minx_popbox + ((popxvals[i][1] + (slist[4][4][i][3]-slist[4][4][i][1]))/maxwide))
        if confint[i][1] > farright:
            farright = confint[i][1]
        popbox.append([[],[]])
        popbox[i][0].append(minx_popbox + popxvals[i][0]/maxwide)
        popbox[i][1].append(minx_popbox + popxvals[i][1]/maxwide)
        if poptree[i][1] == -1 :
            popbox[i][0].append(lineINFy)
        else :
            popbox[i][0].append(ty[poptree[i][1]-1][0])
        if poptree[i][0] == 0:
            popbox[i][1].append(line0y)
        else :
            popbox[i][1].append(ty[poptree[i][0]-1][0])
    return popbox,maxwide, confint, farright

def printpopbox(popbox,maxwide,confint,slist,plist,numpops, rootpop, poptree, ty,scaledpop) :
    """ print popbox representing populations in different time periods """
    global dashinterval
    if simplecolor:
        color = blue
    else:
        color = black
    cdim = []
    for i in range(2*numpops-1):
## look at this crazy go around to make a copy of popbox and change it without changing popbox
        shadowbox = []
        for j in range(len(popbox[i])):
            shadowbox.append([])
            shadowbox[j].extend(popbox[i][j])
        shadowbox[1][0] = popbox[i][1][0] - (slist[4][4][i][1]-slist[4][4][i][2])/maxwide
        w("%%begin left confidence for box %d" % i)
        cdim.append(curvebox(-1,shadowbox,1.5,color,graylevel,i,dash=dashinterval))
        w("%%done left confidence for box %d" % i)
        shadowbox = []
        for j in range(len(popbox[i])):
            shadowbox.append([])
            shadowbox[j].extend(popbox[i][j])
        shadowbox[1][0] = popbox[i][1][0] + (slist[4][4][i][3]-slist[4][4][i][1])/maxwide
        w("%%begin right confidence for box %d" % i)
        cdimtemp =curvebox(cdim[i],shadowbox,1.5,color, graylevel,i,dash=dashinterval)
        w("%%done right confidence for box %d" % i)
    for i in range(2*numpops-1):
        w("%%begin box %d" % i)
        cdimtemp = curvebox(cdim[i],popbox[i],2.5,color,0,i,dash=0)
        w("%%done box %d" % i)
    popprintinc = 0.01
    for i in range(numpops):
        if poptree[i][1] == 1 and i== droppops[1][1] : ## right side of most recent split
            dotext([popbox[i][0][0] + (popbox[i][1][0]-popbox[i][0][0])/2,popbox[i][1][1]+popprintinc],slist[2][4][i],0, False)
        else :
            dotext([popbox[i][0][0],popbox[i][1][1]+popprintinc],slist[2][4][i],0, False)
    popprintinc = 0.025
    if label_a_pops :
        for i in range(numpops,2*numpops-1):
            dotext([max(popbox[i][0][0],popbox[i][0][0] + (popbox[i][1][0] - popbox[i][0][0])/2.0 - popprintinc),\
                popbox[i][0][1] + (popbox[i][1][1] - popbox[i][0][1])/2.0],"pop #"+str(i),0, False)
## plot the confidence arrows for population boxes
    lastperiod = [0]*(2*numpops-1)
    numarrowperiod = [0]*numpops
    for i in range(2*numpops-1):
        for j in range(len(plist)):
            for k in range(len(plist[j])):
                if plist[j][k] == i and j > lastperiod[i]:
                    lastperiod[i] = j
##    print lastperiod
    for i in range(len(lastperiod)):
        numarrowperiod[lastperiod[i]] += 1
    periodposcount = [0]*numpops
    arrowheightinc = 0.006
    arrowheights = []
    for i in range(numpops):
        if i==0 :
            top = line0y
            bot = ty[i][0]
        else:
            top = ty[i-1][0]
            if i== numpops - 1:
                bot = lineINFy
            else :
                bot = ty[i][0]

        if top-bot < 0.1:
            frac = 0.5
        else:
            frac = 0.8
        arrowheights.append(top - (top-bot)*frac)
    for i in range(2*numpops-1):
        period = lastperiod[i]
        arrowheight = max(popbox[i][0][1],arrowheights[period] -periodposcount[period]*2*arrowheightinc)
        head = [confint[i][0],arrowheight]
        tail = [popbox[i][1][0],arrowheight]
        arrowa(head,tail,2,color,graylevel)
        head = [confint[i][1],arrowheight]
        tail = [popbox[i][1][0],arrowheight]
        arrowa(head,tail,0, color, graylevel)
        periodposcount[period] += 1
    if scaledpop != [] :
        ane = scaledpop[rootpop]/1000
        anes = fround(ane)
        dotext([0.15,0.05]," Ancestral Ne (thousands): " + anes,0, False)
    else :
        dotext([0.15,0.05]," Ancestral 4Nu: " + str(slist[4][4][rootpop][1]),0, False)

    if simplecolor:
        w("0 0 0  setrgbcolor")
    return popbox

def set_tlines(ty,numpops,scaledtime, lastt_lower_y):
    """
        line0y - default height of time 0
        eventimes - if True,   space split times evenly
        lastt_lower_y - height of oldest split time,  by default is 1/(numpops+1),   else can be set by user
    """
    tmax = tlowest =  slist[5][4][numpops-2][3] ## bottom of confidence interval of lowest t
    t = []
    for i in range(numpops-1):
        t.append([slist[5][4][i][1],slist[5][4][i][2],slist[5][4][i][3]])  ## [time,  upper ci,  lower ci]
    ty = []
    if localyscale == -1:
        yint = line0y - lastt_lower_y
        for i in range(numpops-1):
            ty.append([])
            if eventimes ==  False:
                for j in range(3):
                    ty[i].append(line0y - (t[i][j]*yint)/tmax)
            else:
                ty[i].append(line0y - ((i+1)/float(numpops+1)*yint)/tmax)
    else :
        timeumean = slist[7][4][1]
        scaleumean = slist[7][4][2]
        for i in range(numpops-1):
            ty.append([])
            for j in range(3):
                ty[i].append(line0y - (t[i][j] * (scaleumean/timeumean/1e6)* localyscale))
                if ty[i][j] < lineINFy :
                    print " time line too low in graph,  reduce local y scale (-y value) "
        lastt_lower_y = ty[numpops-2][2]
##    print "ty  : ",ty
    return ty, lastt_lower_y


def print_tlines(ty,numpops,scaledtime, farright):
    """ print the split time lines and confidence interval lines """
    xinc = 0.005
    if(scaledtime != []):
        if max(scaledtime)/1e6  < 1.0:
            yearscaler = 1e3
            yearscalestring = " KYR"
        else:
            yearscaler = 1e6
            yearscalestring = " MYR"
    if eventimes == False:
        for i in range(numpops-1):
            if (ty[i][1] > ty[i][0]):
                yline(ty[i][1],farright,1,2,graylevel)
            yline(ty[i][0],farright,1,0,0)
            if (ty[i][2] < ty[i][0]):
                yline(ty[i][2],farright,1,2,graylevel)
            if(scaledtime != []):
                scaledtime[i] /= yearscaler
                mtime = round(scaledtime[i],-int(math.log10(scaledtime[i])-2))
                nstr = str(mtime) + yearscalestring
    ##            str(int(round(scaledtime[i],-int(math.log10(scaledtime[i])-2)))) + " yrs"
                dotext([xinc*(i+2),ty[i][0]+0.001],nstr,0, False)
            else :
                nstr = fround(slist[5][4][i][1]) + "tu"
                dotext([xinc*(i+2),ty[i][0]+0.001],nstr,0, False)
            if (ty[i][1] > ty[i][0]):
                arrowa([xinc*(i+1),ty[i][1]],[xinc*(i+1),ty[i][0]],1, black, graylevel)
            if (ty[i][2] < ty[i][0]):
                arrowa([xinc*(i+1),ty[i][2]],[xinc*(i+1),ty[i][0]],3, black, graylevel)
    else:
        for i in range(numpops-1):
            yline(ty[i][0],farright,1,0,0)
            if(scaledtime != []):
                scaledtime[i] /= yearscaler
                mtime = round(scaledtime[i],-int(math.log10(scaledtime[i])-2))
                nstr = str(mtime) + yearscalestring
    ##            str(int(round(scaledtime[i],-int(math.log10(scaledtime[i])-2)))) + " yrs"
                dotext([xinc*(i+2),ty[i][0]+0.001],nstr,0, False)
            else :
                nstr = fround(slist[5][4][i][1]) + "tu"
                dotext([xinc*(i+2),ty[i][0]+0.001],nstr,0, False)
    return ty

def print_mcurves(slist,numpops, popbox, plist, color):
    """migration arrows:
    note - migration arrows are drawn in the forward direction!!
    likelihood ratio=ratio of the highest probability to the probability at 2NM = 0
    Sinficant likelihood ratios:
    2.70554  at p=0.05   The ratio of probabilities (as opposed to twice the log ratio) is 3.86813
    5.41189	  at p = 0.01  the ratio of prbabilities is 14.9685
    9.54954	 at p = 0.001  the ration of probabilities is 118.483
    3.86813 <= ratio <= 14.9685 upper arrow is a dash  (0.95 on chi square 50% 0.0 and 50% 1df)
    14.9685 <= ratio <= 118.483  upper arrow is a dotted (0.99 on chi square 50% 0.0 and 50% 1df)
    118.483 <= ratio upper arrow is a solid line       (0.999 on chi square 50% 0.0 and 50% 1df)

    list of things in miginfo[i]
    0 topop
    1 frompop
    2 direction
    3 period
    4 the number in this period
    5 2NM est
    6 log likelihood ratio stat
    also save # events to print in the period"""
    def checkm(val2NM, llr):
        return  (moption == 'a' and val2NM > min2NM) or \
               (moption == 's' and llr >= 2.74) or \
               val2NM > moption

    mperiodnum = [0]*(numpops-1)
    if len(slist[6]) > 4:
        sml = slist[6][4]
        miginfo = []
        mi = 0
        for i in range(len(sml)):
##            pratio =  sml[i][3]/sml[i][2]
##            llr = 2*math.log(pratio)
## alternate code to get values from Marginal peak location tables
            llr = sml[i][2]


            if checkm(sml[i][1],llr) :
                miginfo.append([])
                c1 = max(sml[i][0].find("M"),sml[i][0].find("m")) ## either upper of lower case
                c2 = sml[i][0].find(">")
                miginfo[mi].append(int(sml[i][0][c2+1:len(sml[i][0])]))
                miginfo[mi].append(int(sml[i][0][c1+1:c2]))
                found1 = False
                found2 = False
                p  = 0
                while 1 :
                    for j in range(len(plist[p])):
                        if plist[p][j] == miginfo[mi][0]:
                            found1 = True
                            if found2 :
                                direction = 2
                            else:
                                direction = 0
                        if  plist[p][j] == miginfo[mi][1]:
                            found2 = True
                    if found1 and found2 :
                        break
                    else:
                        p += 1
                miginfo[mi].append(direction)
                miginfo[mi].append(p)
                miginfo[mi].append(mperiodnum[p])
                mperiodnum[p] += 1
                miginfo[mi].append(sml[i][1])
                miginfo[mi].append(llr)
                mi += 1

        mboxfrac = 0.3
        ## set height of curves
        y = []
        for i in range(len(miginfo)):
            frompop = miginfo[i][0]
            period = miginfo[i][3]
            hi = popbox[frompop][1][1]
            for j in range (len(plist[period])):
                if hi > popbox[plist[period][j]][1][1] :
                    hi = popbox[plist[period][j]][1][1]
            lo = 0
            for j in range (len(plist[period])):
                if lo < popbox[plist[period][j]][0][1] :
                    lo = popbox[plist[period][j]][0][1]
            y.append(hi - (hi - lo)*(miginfo[i][4]+1)/(mperiodnum[miginfo[i][3]]+1))
        for i in range(len(miginfo)):
            frompop = miginfo[i][0]
            topop = miginfo[i][1]
            period = miginfo[i][3]
            direc = miginfo[i][2]
            val2NM = fround(miginfo[i][5])
            if miginfo[i][6] >= 2.70554 and miginfo[i][6] < 5.41189 :
                val2NM += "*"
            if miginfo[i][6] >= 5.41189 and miginfo[i][6] < 9.54954 :
                val2NM += "**"
            if miginfo[i][6] >= 9.54954 :
                val2NM += "***"
            text2NMwidth = textwide(val2NM,2.5)
            if direc == 0 :
                tailx =  popbox[frompop][1][0] - (popbox[frompop][1][0]-popbox[frompop][0][0])*mboxfrac
                headx =  popbox[topop][0][0] + (popbox[topop][1][0] - popbox[topop][0][0]) * mboxfrac
                if (text2NMwidth > abs(tailx-headx)):
                    tailx -= (text2NMwidth - abs(tailx-headx))/2
                    headx += (text2NMwidth - abs(tailx-headx))/2
            if direc == 2:
                tailx =  popbox[frompop][0][0] + (popbox[frompop][1][0] - popbox[frompop][0][0]) * mboxfrac
                headx =  popbox[topop][1][0] - (popbox[topop][1][0]-popbox[topop][0][0])* mboxfrac
                if (text2NMwidth > abs(tailx-headx)):
                    tailx += (text2NMwidth - abs(tailx-headx))/2
                    headx -= (text2NMwidth - abs(tailx-headx))/2
            migrationcurvearrow(val2NM,[headx,y[i]],[tailx,y[i]],direc,red)


##***********************************************************************************
##////////////// Command line use ///////////////////////////////////////////////////
##***********************************************************************************

def scancommandline():
    """ command line consists of flags, each with a dash, '-', followed immediately by a letter
        some flags should be followed by a value, depending on the flag.  The value can be placed
        immediately after the flag or spaces can be inserted """

    def aflag ():
        global label_a_pops
        label_a_pops = True
    def bflag (tempval):
        global popboxspaceadj
        popboxspaceadj = float(tempval)
    def dflag ():
        global skipdemographicscaling
        skipdemographicscaling  =  True
    def eflag():
        global eventimes
        eventimes = True
    def iflag (tempname):
        global imfilename
        imfilename = tempname
    def oflag (tempname):
        global outputfilename
        outputfilename= tempname
    def gflag (tempval):
        global globalscale
        globalscale = float(tempval)
    def xflag (tempval):
        global localxscale
        localxscale = float(tempval)
    def yflag (tempval):
        global  localyscale
        localyscale = float(tempval)
    def hflag (tempval):
        global arrowheightadj
        arrowheightadj = float(tempval)
    def fflag(tempval):
        global font, bifont
        font = tempval
        bifont = font + "-BoldItalic"
    def mflag(tempval):
        global moption
        if tempval[0].isdigit():
            moption = float(tempval)
        else:
            moption = tempval
    def pflag(tempval):
        global fontsize
        global fontfixed
        fontsize = float(tempval)
        fontfixed = True
    def tflag(tempval):
        global lastt_lower_y
        global set_lastt_lower_y
        lastt_lower_y = float(tempval)
        set_lastt_lower_y = False
    def sflag ():
        global dosquare
        global maximumxpoint
        dosquare = True
        maximumxpoint = 576.1
    def uflag ():
        global simplecolor
        simplecolor  = True
    def vflag ():
        global rgbcolor
        rgbcolor = True
    def removewhitespace(temps):
        return "".join(temps.split())

    def cleanarglist(arglist,flags_with_values,flags_without_values):
        newarg = []
        if arglist[0][0] != "-":  # skip program name at beginning of list
            arglist = arglist[1:]
        ai  = 0
        while ai < len(arglist):
            if removewhitespace(arglist[ai]) != "":
                arglist[ai] = removewhitespace(arglist[ai])
            else:
                print "bad whitespace in command line: ",repr(" ",join(arglist))
                sys.exit(1)
            if arglist[ai][0] == '-' :
                if arglist[ai][1] in flags_with_values  and len(arglist[ai])==2:  ## found a space in the command line
                    arglist[ai] = arglist[ai] + arglist[ai+1]
                    newarg.append(arglist[ai])
                    ai += 1
                else:
                    newarg.append(arglist[ai])
            else:
                print "error on command line,  \"-\" not found:",arglist[ai]
                sys.exit(1)
            ai += 1

        return newarg

    def checkallflags(flags_with_values,flags_withoutvalues,cldic):
        """
            checks that flags_with_values,flags_withoutvalues and cldic all make use of the appropriate flags
        """
        if len(set(flags_with_values).intersection(set(flags_without_values))) > 0:
            print "error some flags appear in two lists of flags,  with and without required values:",set(flags_with_values).intersection(set(flags_without_values))
            sys.exit(1)
        for flag in set(flags_with_values).union(set(flags_withoutvalues)):
            if flag not in cldic:
                print "error some flag mismatch between strings of flags and dictionary of flags:",flag
                sys.exit(1)
        return

    cldic = {'a':aflag,'b':bflag,'d':dflag,'e':eflag,'f':fflag,\
             'g':gflag,'h':hflag,'i':iflag,'m':mflag,'o':oflag,\
             'p':pflag, 's':sflag, 't':tflag,'u':uflag,'v':vflag,\
             'x':xflag,'y':yflag}
    flags_with_values =  "bfghimoptxy"
    flags_without_values = "adesuv"
    checkallflags(flags_with_values,flags_without_values,cldic)
    argv = cleanarglist(sys.argv,flags_with_values,flags_without_values)
    for i in range(0,len(argv)):
        if argv[i][0] == '-' :
            flaglet = argv[i][1].lower()
##            print i, flaglet
            if len(argv[i]) == 2 :
                if i == (len(argv)-1):
                    cldic[flaglet]()
                else :
                    if  argv[i+1][0] == '-' :
                        cldic[flaglet]()
                    else :
                        cldic[flaglet](argv[i+1])
                        i += 1
            else :
                if (len(argv[i]) < 2):
                    print "problem on command line "
                    exit()
                cldic[flaglet](argv[i][2:len(argv[i])])
        else:
            print "error on command line,  \"-\" not found:",argv[i]
            sys.exit(1)

def printcommandset():
    print "IMfig command line terms:"
    print "-a include ancestral population #'s in plot"
    print "-b adjust width spacing of population boxes, values > 0, default = 1"
    print "-d do not use demographic scale information even if in input file"
    print "-e space split times evenly  (not proportional to time,  no confidence intervals shown)"
    print "-f font.  Default=Arial. Use postscript fonts available on the computer"
    print "   e.g. Arial, Helvetica, Times-roman, Courier"
    print "-g global plot scale sets the size of the plot, max = 1, default = 1"
    print "-h arrow width, default = 1"
    print "-i input file name"
    print "-m migration (2NM) arrow option:"
    print "      -ma : arrow printed for all 2NM > 0"
    print "      -ms : arrows only when 2NM is statistically significant (default)"
    print "      -m# : '#' is a number, arrows printed when 2NM >= # (e.g. -m0.1)"
    print "-o output file name, e.g. -o myoutputfile.eps, default=im_eps_file.eps"
    print "-p fontsize (default is 14 for full scale, default follows global scale)"
    print "-s print square, rather than landscape"
    print "-t relative height of oldest time point, values between 0 and 1"
    print "     default value = 1/(# sampled populations+1)"
    print "-u simple colors, blue for population boxes, red arrows for migration (default grayscale)"
    print "-v multiple colors for population boxes, red arrows for migration (default grayscale)"
    print "-x adjust width of plot,  >1 means wider, <1 means narrower"
    print "-y adjust height of splittimes, relative to bottom of figure, max = 1."  ## not clear what this does  5/12/2016



##*************************************************************
##///////////// default values, basic scale////////////////////
##*************************************************************


def setbasexyscale():
    global maximumxpoint, maximumypoint, maxll, maxur
    minimumxpoint = minimumypoint = 36.1   #forgot where this came from
    maxll = [minimumxpoint,minimumypoint]
    maxur = [maximumxpoint,maximumypoint]

def setdefaults():
    global numpops, label_a_pops, simplecolor, dosquare, imfilename, outputfilename
    global globalscale, font,bifont, fontsize, fontfixed, line0y, lineINFy, localxscale
    global localyscale, localxscale, localyscale, arrowheightadj
    global maximumxpoint, maximumypoint
    global lastt_lower_y, set_lastt_lower_y, slist, blue, red, black, graylevel
    global popboxspaceadj, moption, skipdemographicscaling
    global eventimes
    global rgbset,rgbcolor
    global dashinterval
    numpops = 0
    label_a_pops = False
    simplecolor = False
    dosquare = False
    eventimes = False
    imfilename = "im_eps.txt"
    outputfilename = "im_eps_file"
    globalscale = 1
    font = "Arial"
    bifont = "Arial-BoldItalic"
    fontsize = 14
    fontfixed = False
    line0y = 0.95   ## height of time 0
    lineINFy = 0.1  ## height of time infinity
    localxscale = -1
    localyscale = -1
    arrowheightadj = 1
    ## lower left and upper right corners of an 11x8.5 inch (landscape) page, with roughtly 1/2" margins
    maximumxpoint = 756.1
    maximumypoint = 576.1
    lastt_lower_y = -1
    set_lastt_lower_y = True
    slist = []
    blue = [0,0,1]
    red = [1,0,0]
    black = [0,0,0]
    graylevel = 0.6
    popboxspaceadj = 1.0
    moption = 's'
    skipdemographicscaling = False
    rgbcolor = False
    rgbset = [[0.8,0,0],\
                [0.6,0.4,0],\
                [0.6,0.6,0],\
                [0.6,0,0.4],\
                [0.6,0,0.6],\
                [0.0,0.8,0],\
                [0.0,0.6,0.4],\
                [0.0,0.6,0.6],\
                [0.0,0.4,0.6],\
                [0.6,0.4,0],\
                [0.0,0,0.8],\
                [0.4,0,0.6],\
                [0.8,0.0,0.0],\
                [0.6,0.4,0],\
                [0.6,0.6,0],\
                [0.6,0,0.4],\
                [0.6,0,0.6],\
                [0.0,0.8,0],\
                [0.0,0.6,0.4],\
                [0.0,0.6,0.6],\
                [0.0,0.4,0.6],\
                [0.6,0.4,0],\
                [0.0,0,0.8],\
                [0.4,0,0.6]]   ## just a long list of colors to use,  list repeats just to make it longer than is likely to be needed
    dashinterval = 3

##***********************************************************************************
##////////////// MAIN PROGRAM ///////////////////////////////////////////////////////
##***********************************************************************************

##IMfig can be run from within a python interpreter such as IDLE,  or from the command
##line if python is installed.
##To run from the command line include the path to the imfig program in the call to python
##e.g. python "C:\Documents and Settings\hey\My Documents\genemod\ML-MCMC\SEAI\IMa2\IMfig\imfig.py"

## Ariel is the default font

print "IMfig3 program.  Copyright 2009-2016  Jody Hey "
setdefaults()

cmdstr = ""
cmdstr = r"IMfig3.py -iBaHzSwYr_100loci_mpi_20b.out -odebugteven.eps " + "\n" + " " +  "\r" + "  -t 0.1  -e -u -ma"
cmdstr = r"IMfig3.py -inoPan_v2_tot4_expo_mprior_1_5_2012.out -onoPan_v2_tot4_expo_mprior_1_5_2012.eps -d -g1.0 -b10 -u -v"
cmdstr = r"IMfig3.py -iPan_4pops_w_names_3_9_09_5_15_09_m1_reload_8_30_09.out -oPan_4pops_w_names_3_9_09_5_15_09_m1_reload_8_30_09.eps -b2 -v "
##cmdstr = ""
##cmdstr = "IMfig3.py -iPan_troglodytes_3pops_3_9_09_5loci_test4.out -odebug.eps -c "
##cmdstr = ""


##***** identify if program is run within interpreter, or from command line ***********
if len(sys.argv)<=1 : ## true if not run from command line with commands given on that line, use this so can run in IDLE and in cmd window
    sys.argv =cmdstr.split()  ## use the line defined in the program
if len(sys.argv)<=1 :
    printcommandset()
    sys.exit()

##////////////// get info from the command line ///////////////////
scancommandline()
sys.argv = []
print "input file: %s\noutput file %s" % (imfilename, outputfilename)

##////////////// get info from the input file (i.e. the IM results files) ///////////////////
print "read inputfile"
(numpops,slist,scaledpop,scaledtime) = readimfile(imfilename)
(poptree,rootpop,poptreestring,plist, droppops,addpop) = poptreeread(slist[3][4],numpops)

##//////////////// set scales ///////////////////////////
print "set scales"
setbasexyscale()
if set_lastt_lower_y :
    lastt_lower_y = 1.0/(numpops + 1)
(ty, lastt_lower_y) = set_tlines(slist,numpops, scaledtime, lastt_lower_y)
wadjust = ""
for i in range(numpops-1):
    wadjust += "00"
if(scaledtime != []):
    minx_popbox = textwide(wadjust+"0.00 MYR", tfactor)
else :
    minx_popbox = textwide(wadjust+"0.00 tu", tfactor)

minx_popbox /= globalscale
if localxscale > 0 :
    minx_popbox /= localxscale
(popbox,maxwide,confint, farright) = setpopbox(ty,slist,numpops)


##//////////////// write the output file ///////////////////////////
epsname = outputfilename+'.eps'
epsf = file(epsname,"w")
w("%!PS-Adobe-3.0 EPSF-3.0")
w("%%legal size in landscape is 792x612 set bounding box with 0.5inch margins")
w("%%the lower corner is at 36 36 x dim is 720 wide  y dim is 540 hi")
w("%%%%BoundingBox: %d %d  %d  %d" % (int(maxll[0]),int(maxll[1]),int(maxur[0]),int(maxur[1])))
w("%%%%IMfig3 program author: Jody Hey   Copyright 2009-2016")
w("%%%%Command line for IMfig3 program that generated this file: %s"%cmdstr)
#### useful for debugging, include this DrawAnX function in the code
##w("/DrawAnX")
##w("{ 3 3 rmoveto -6 -6 rlineto")
##w("0 6 rmoveto 6 -6 rlineto")
##w("0.01 setlinewidth")
##w("stroke } def")
#### use by calling and passing x and y values
####e.g. w("%f %f moveto DrawAnX" %(point[0],point[1]))

print "make figure"
print "splitting times"
ty = print_tlines(ty,numpops, scaledtime, farright)
print "population boxes"
popbox = printpopbox(popbox,maxwide,confint,slist,plist,numpops, rootpop, poptree, ty, scaledpop)
print "migration arrows"
print_mcurves(slist,numpops, popbox, plist, simplecolor)
epsf.close()
from PIL import Image
tempf = Image.open(epsname)
jpgname = outputfilename+'.jpg'
jpgbigname = outputfilename+'_hires.jpg'
tempf.save(jpgname)
bigf = Image.open(epsname)
bigf.load(scale=3)
bigf.save(jpgbigname)

print "plot completed"



