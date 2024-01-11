import os 
import pya

import misc_002              as misc
import snapHandler_002       as snHdl
import markerHandler_002     as mkHdl
import markerTheme_002       as mkThm 
import objInRangeHandler_001 as oirHdl

class HoverRulerPlugin(pya.Plugin):
    def __init__(self, view):
        super(HoverRulerPlugin, self).__init__()
        self.snapResult    = snHdl.SnapResults()
        self.initiallize(view)
               
    def initiallize(self, view):        
        self.view            = view
        self.snapHandler     = snHdl.SnapHandler(self.view)        
        self.objInRngHdl     = oirHdl.ObjInRangeHandler(self.view)
        self.markerManager   = mkHdl.MarkerManager([self.snapHandler])
              
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
                       
    def mouse_click_event(self, p, buttons, prio):
        if prio:
            if (buttons & misc.Keys.left):
                   
                snapPoint   = self.snapResult.snapPoint
                snappedEdge = self.snapResult.snappedEdge
          
                if snappedEdge:
                    ruler        = pya.Annotation()   
                    ruler.points = [snappedEdge.p1, snappedEdge.p2]
                    self.view.insert_annotation(ruler)   
                else:
                    self.view.create_measure_ruler(snapPoint)

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
            self.snapResult = snapResult
            if snappedEdge:
                self.snapHandler.markPropsAppend(mkThm.textMark(snapPoint, f"  {round(snappedEdge.length(), digit)}", 0))
                
            self.markerManager.updateAll()
            return True
        return False
        
if __name__ == "__main__":
    view = pya.Application.instance().main_window().current_view() 
    HoverRulerPlugin(view)