import os 
import pya
import math
import misc_002              as misc
import snapHandler_002       as snHdl
import markerHandler_002     as mkHdl
import markerTheme_002       as mkThm 
import objInRangeHandler_001 as oirHdl

# from PyQt5.QtCore import QObject, QEvent



class HoverRulerPlugin(pya.Plugin):
    def __init__(self, view):
        super(HoverRulerPlugin, self).__init__()
        self.snapResult    = snHdl.SnapResults()
        self.catcher = None
        self.initiallize(view)
               
    def initiallize(self, view):        
        self.view            = view
        self.snapHandler     = snHdl.SnapHandler(self.view)        
        self.objInRngHdl     = oirHdl.ObjInRangeHandler(self.view)
        self.markerManager   = mkHdl.MarkerManager([self.snapHandler])
        self.annotation_mode = 0
              
    def activated(self):
        self.initiallize(self.view)
        
    def deactivated(self):
        self.markerManager.clearAll()
        self.markerManager.updateAll()
        self.initiallize(self.view)
        self.ungrab_mouse()
            
    def deactive(self):
        keyPress = pya.QKeyEvent(pya.QKeyEvent.KeyPress, 16777216, pya.Qt.NoModifier)
        pya.QApplication.sendEvent(self.view.widget(), keyPress)   

    def hoverAngle(self, snappedShape,  snappedVertex):  
        v1, v2 = [(e.p1-e.p2) * (1 if e.p2 == snappedVertex else -1) for e in snappedShape.each_edge() if e.contains(snappedVertex)] [0:2]
        armLen = min([v1.length(), v2.length(), misc.dPixelLength(self.view, 80)])
        v1i    = misc.vertorLengthen(v1, armLen)
        v2i    = misc.vertorLengthen(v2, armLen)
        angle  = misc.vectorAngle(v1, v2)
        angle  = (360 - angle) if (angle > 180) else angle
        
        n      = 32         
        p1     = snappedVertex + v1i
        p2     = snappedVertex
        p3     = snappedVertex + v2i
        chk    = pya.DEdge(p2, p2 + misc.vectorRotate(v1i, (angle / 2 )))
        cord   = pya.DEdge(p3, p1)
        d      = 1 if cord.intersects(chk) else -1
        pa     = [ p2 + 0.7 * misc.vectorRotate(v1i, (angle / n * i *d)) for i in range(n + 1)] 
        return p1, p2, p3, pa, angle
    

                  
    def mouse_click_event(self, p, buttons, prio):
        if prio:
            if (buttons & misc.Keys.left):
                snapResult      = self.snapResult
                snapPoint       = snapResult.snapPoint
                snappedEdge     = snapResult.snappedEdge
                snappedVertex   = snapResult.snappedVertex
                snappedShape    = snapResult.snappedShape

                self.view.transaction("add ruler")
                #temporary, later should be merge and handled by RulerManager
                try:
                    if snappedEdge:
                        ruler         = pya.Annotation()   
                        ruler.points  = [snappedEdge.p1, snappedEdge.p2]
                        self.view.insert_annotation(ruler)  
     
                    elif snappedVertex:
                        p1, p2, p3, pa, angle = self.hoverAngle( snappedShape, snappedVertex)
                        p1 = (p1 - p2) * 0.8 + p2
                        p3 = (p3 - p2) * 0.8 + p2
                        ruler         = pya.Annotation()   
                        ruler.style   = pya.Annotation.StyleLine
                        ruler.outline = pya.Annotation.OutlineAngle
                        ruler.points  = [p1, p2, p3]
                        ruler.fmt     = "$(sprintf('%.5g',G))°"
                        self.view.insert_annotation(ruler)  
                             
                    else:
                        self.view.create_measure_ruler(snapPoint)
                        
                finally : self.view.commit()
            elif (buttons & misc.Keys.right):
                self.annotation_mode = (self.annotation_mode + 1) % 4
            return True
        return False   
                
    def mouse_moved_event(self, p, buttons, prio):
        if prio:
            digit           = misc.viewDigit(self.view)
            searchRange     = min([misc.dPixelLength(self.view, 25), 50])
            sizeLimit       = misc.dPixelLength(self.view, 5)
            rangeDBox       = pya.DBox(pya.DPoint(p.x - searchRange, p.y - searchRange),pya.DPoint(p.x + searchRange, p.y + searchRange))
            hoverShapes     = self.objInRngHdl.visibleShapeInCVRange(rangeDBox, sizeLimit) 
            snapResult      = self.snapHandler.snapToObject(p, searchRange, hoverShapes)
            snapPoint       = snapResult.snapPoint
            snappedEdge     = snapResult.snappedEdge
            snappedVertex   = snapResult.snappedVertex
            snappedShape    = snapResult.snappedShape
            self.snapResult = snapResult
            
            if snappedEdge:
                if self.annotation_mode == 0:
                    self.snapHandler.markPropsAppend(mkThm.textMark(snapPoint, f" d = {round(snappedEdge.length(), digit)}", 0))
                elif self.annotation_mode == 1:
                    self.snapHandler.markPropsAppend(mkThm.textMark(snapPoint, f" dx = {round(snappedEdge.dx(), digit)}, dy = {round(snappedEdge.dy(), digit)}", 0))
                elif self.annotation_mode == 2:
                    self.snapHandler.markPropsAppend(mkThm.textMark(snapPoint, f" a = {round(math.atan2(abs(snappedEdge.dy()),abs(snappedEdge.dx()))*180/math.pi, digit)}", 0))
                else:
                    self.snapHandler.markPropsAppend(mkThm.textMark(snapPoint, f" 90-a = {round(90 - math.atan2(abs(snappedEdge.dy()),abs(snappedEdge.dx()))*180/math.pi, digit)}", 0))
            
            if snappedVertex:
            
                p1, p2, p3, pa, angle = self.hoverAngle( snappedShape,  snappedVertex)
                
                self.snapHandler.markPropsAppend([
                    [ mkHdl.MarkerTemplate(data = pya.DEdge(p1, p2), line_width = 1, line_style = 0, vertex_size = 0)],
                    [ mkHdl.MarkerTemplate(data = pya.DEdge(p2, p3), line_width = 1, line_style = 0, vertex_size = 0)],
                    [ mkHdl.MarkerTemplate(data = pya.DPath(pa,  0), line_width = 1, line_style = 3, vertex_size = 0)],
                    
                ])
                
                self.snapHandler.markPropsAppend(mkThm.textMark(snapPoint, f"  {round(angle, 2)}°", 0))

            
            self.markerManager.updateAll()
            return True
        return False
        
if __name__ == "__main__":
    view = pya.Application.instance().main_window().current_view() 
    if view:
        HoverRulerPlugin(view)