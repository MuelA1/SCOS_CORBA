# Python stubs generated by omniidl from IEV_PRO.idl
# DO NOT EDIT THIS FILE!

import omniORB, _omnipy
from omniORB import CORBA, PortableServer
_0_CORBA = CORBA


_omnipy.checkVersion(4,2, __file__, 1)

try:
    property
except NameError:
    def property(*args):
        return None


# #include "IBASE.idl"
import IBASE_idl
_0_IBASE = omniORB.openModule("IBASE")
_0_IBASE__POA = omniORB.openModule("IBASE__POA")

# #include "ITM.idl"
import ITM_idl
_0_ITM = omniORB.openModule("ITM")
_0_ITM__POA = omniORB.openModule("ITM__POA")

# #include "IEV.idl"
import IEV_idl
_0_IEV = omniORB.openModule("IEV")
_0_IEV__POA = omniORB.openModule("IEV__POA")

# #include "ICLOCK.idl"
import ICLOCK_idl
_0_ICLOCK = omniORB.openModule("ICLOCK")
_0_ICLOCK__POA = omniORB.openModule("ICLOCK__POA")

# #include "IBASE_IF.idl"
import IBASE_IF_idl
_0_IBASE_IF = omniORB.openModule("IBASE_IF")
_0_IBASE_IF__POA = omniORB.openModule("IBASE_IF__POA")

# #include "ICLOCK_PRO.idl"
import ICLOCK_PRO_idl
_0_ICLOCK_PRO = omniORB.openModule("ICLOCK_PRO")
_0_ICLOCK_PRO__POA = omniORB.openModule("ICLOCK_PRO__POA")

#
# Start of module "IEV_PRO"
#
__name__ = "IEV_PRO"
_0_IEV_PRO = omniORB.openModule("IEV_PRO", r"IEV_PRO.idl")
_0_IEV_PRO__POA = omniORB.openModule("IEV_PRO__POA", r"IEV_PRO.idl")


# forward interface EventMngrView;
_0_IEV_PRO._d_EventMngrView = (omniORB.tcInternal.tv_objref, "IDL:IEV_PRO/EventMngrView:1.0", "EventMngrView")
omniORB.typeMapping["IDL:IEV_PRO/EventMngrView:1.0"] = _0_IEV_PRO._d_EventMngrView

# interface EventMngr
_0_IEV_PRO._d_EventMngr = (omniORB.tcInternal.tv_objref, "IDL:IEV_PRO/EventMngr:1.0", "EventMngr")
omniORB.typeMapping["IDL:IEV_PRO/EventMngr:1.0"] = _0_IEV_PRO._d_EventMngr
_0_IEV_PRO.EventMngr = omniORB.newEmptyClass()
class EventMngr (_0_IBASE_IF.Model):
    _NP_RepositoryId = _0_IEV_PRO._d_EventMngr[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_IEV_PRO.EventMngr = EventMngr
_0_IEV_PRO._tc_EventMngr = omniORB.tcInternal.createTypeCode(_0_IEV_PRO._d_EventMngr)
omniORB.registerType(EventMngr._NP_RepositoryId, _0_IEV_PRO._d_EventMngr, _0_IEV_PRO._tc_EventMngr)

# EventMngr operations and attributes
EventMngr._d_registerEventView = ((omniORB.typeMapping["IDL:IEV_PRO/EventMngrView:1.0"], omniORB.typeMapping["IDL:IEV/TransmissionFilter:1.0"]), (omniORB.tcInternal.tv_long, ), None)
EventMngr._d_unregisterEventView = ((omniORB.tcInternal.tv_long, ), (omniORB.tcInternal.tv_boolean, ), None)
EventMngr._d_registerEvents = ((omniORB.tcInternal.tv_long, omniORB.typeMapping["IDL:IEV/EventFilter:1.0"]), (omniORB.tcInternal.tv_boolean, ), None)
EventMngr._d_unregisterEvents = ((omniORB.tcInternal.tv_long, ), (omniORB.tcInternal.tv_boolean, ), None)
EventMngr._d_modifyEventFilter = ((omniORB.tcInternal.tv_long, omniORB.typeMapping["IDL:IEV/EventFilter:1.0"]), (omniORB.tcInternal.tv_boolean, ), None)
EventMngr._d_registerOOLs = ((omniORB.tcInternal.tv_long, omniORB.typeMapping["IDL:IEV/OOLinfoFilter:1.0"]), (omniORB.tcInternal.tv_boolean, ), None)
EventMngr._d_unregisterOOLs = ((omniORB.tcInternal.tv_long, ), (omniORB.tcInternal.tv_boolean, ), None)
EventMngr._d_modifyOOLfilter = ((omniORB.tcInternal.tv_long, omniORB.typeMapping["IDL:IEV/OOLinfoFilter:1.0"]), (omniORB.tcInternal.tv_boolean, ), None)
EventMngr._d_modifyTransmissionFilter = ((omniORB.tcInternal.tv_long, omniORB.typeMapping["IDL:IEV/TransmissionFilter:1.0"]), (omniORB.tcInternal.tv_boolean, ), None)
EventMngr._d_getFullData = ((omniORB.tcInternal.tv_long, ), (omniORB.typeMapping["IDL:IEV/CombinedEvents:1.0"], ), {_0_ICLOCK.NotPossible._NP_RepositoryId: _0_ICLOCK._d_NotPossible})
EventMngr._d_getNextData = ((omniORB.tcInternal.tv_long, ), (omniORB.typeMapping["IDL:IEV/CombinedEvents:1.0"], ), {_0_ICLOCK.NotPossible._NP_RepositoryId: _0_ICLOCK._d_NotPossible})

# EventMngr object reference
class _objref_EventMngr (_0_IBASE_IF._objref_Model):
    _NP_RepositoryId = EventMngr._NP_RepositoryId

    def __init__(self, obj):
        _0_IBASE_IF._objref_Model.__init__(self, obj)

    def registerEventView(self, *args):
        return self._obj.invoke("registerEventView", _0_IEV_PRO.EventMngr._d_registerEventView, args)

    def unregisterEventView(self, *args):
        return self._obj.invoke("unregisterEventView", _0_IEV_PRO.EventMngr._d_unregisterEventView, args)

    def registerEvents(self, *args):
        return self._obj.invoke("registerEvents", _0_IEV_PRO.EventMngr._d_registerEvents, args)

    def unregisterEvents(self, *args):
        return self._obj.invoke("unregisterEvents", _0_IEV_PRO.EventMngr._d_unregisterEvents, args)

    def modifyEventFilter(self, *args):
        return self._obj.invoke("modifyEventFilter", _0_IEV_PRO.EventMngr._d_modifyEventFilter, args)

    def registerOOLs(self, *args):
        return self._obj.invoke("registerOOLs", _0_IEV_PRO.EventMngr._d_registerOOLs, args)

    def unregisterOOLs(self, *args):
        return self._obj.invoke("unregisterOOLs", _0_IEV_PRO.EventMngr._d_unregisterOOLs, args)

    def modifyOOLfilter(self, *args):
        return self._obj.invoke("modifyOOLfilter", _0_IEV_PRO.EventMngr._d_modifyOOLfilter, args)

    def modifyTransmissionFilter(self, *args):
        return self._obj.invoke("modifyTransmissionFilter", _0_IEV_PRO.EventMngr._d_modifyTransmissionFilter, args)

    def getFullData(self, *args):
        return self._obj.invoke("getFullData", _0_IEV_PRO.EventMngr._d_getFullData, args)

    def getNextData(self, *args):
        return self._obj.invoke("getNextData", _0_IEV_PRO.EventMngr._d_getNextData, args)

omniORB.registerObjref(EventMngr._NP_RepositoryId, _objref_EventMngr)
_0_IEV_PRO._objref_EventMngr = _objref_EventMngr
del EventMngr, _objref_EventMngr

# EventMngr skeleton
__name__ = "IEV_PRO__POA"
class EventMngr (_0_IBASE_IF__POA.Model):
    _NP_RepositoryId = _0_IEV_PRO.EventMngr._NP_RepositoryId


    _omni_op_d = {"registerEventView": _0_IEV_PRO.EventMngr._d_registerEventView, "unregisterEventView": _0_IEV_PRO.EventMngr._d_unregisterEventView, "registerEvents": _0_IEV_PRO.EventMngr._d_registerEvents, "unregisterEvents": _0_IEV_PRO.EventMngr._d_unregisterEvents, "modifyEventFilter": _0_IEV_PRO.EventMngr._d_modifyEventFilter, "registerOOLs": _0_IEV_PRO.EventMngr._d_registerOOLs, "unregisterOOLs": _0_IEV_PRO.EventMngr._d_unregisterOOLs, "modifyOOLfilter": _0_IEV_PRO.EventMngr._d_modifyOOLfilter, "modifyTransmissionFilter": _0_IEV_PRO.EventMngr._d_modifyTransmissionFilter, "getFullData": _0_IEV_PRO.EventMngr._d_getFullData, "getNextData": _0_IEV_PRO.EventMngr._d_getNextData}
    _omni_op_d.update(_0_IBASE_IF__POA.Model._omni_op_d)

EventMngr._omni_skeleton = EventMngr
_0_IEV_PRO__POA.EventMngr = EventMngr
omniORB.registerSkeleton(EventMngr._NP_RepositoryId, EventMngr)
del EventMngr
__name__ = "IEV_PRO"

# interface EventMngrView
_0_IEV_PRO._d_EventMngrView = (omniORB.tcInternal.tv_objref, "IDL:IEV_PRO/EventMngrView:1.0", "EventMngrView")
omniORB.typeMapping["IDL:IEV_PRO/EventMngrView:1.0"] = _0_IEV_PRO._d_EventMngrView
_0_IEV_PRO.EventMngrView = omniORB.newEmptyClass()
class EventMngrView (_0_IBASE_IF.View):
    _NP_RepositoryId = _0_IEV_PRO._d_EventMngrView[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_IEV_PRO.EventMngrView = EventMngrView
_0_IEV_PRO._tc_EventMngrView = omniORB.tcInternal.createTypeCode(_0_IEV_PRO._d_EventMngrView)
omniORB.registerType(EventMngrView._NP_RepositoryId, _0_IEV_PRO._d_EventMngrView, _0_IEV_PRO._tc_EventMngrView)

# EventMngrView operations and attributes
EventMngrView._d_notifyEvents = ((omniORB.typeMapping["IDL:IEV/CombinedEvents:1.0"], ), (), None)

# EventMngrView object reference
class _objref_EventMngrView (_0_IBASE_IF._objref_View):
    _NP_RepositoryId = EventMngrView._NP_RepositoryId

    def __init__(self, obj):
        _0_IBASE_IF._objref_View.__init__(self, obj)

    def notifyEvents(self, *args):
        return self._obj.invoke("notifyEvents", _0_IEV_PRO.EventMngrView._d_notifyEvents, args)

omniORB.registerObjref(EventMngrView._NP_RepositoryId, _objref_EventMngrView)
_0_IEV_PRO._objref_EventMngrView = _objref_EventMngrView
del EventMngrView, _objref_EventMngrView

# EventMngrView skeleton
__name__ = "IEV_PRO__POA"
class EventMngrView (_0_IBASE_IF__POA.View):
    _NP_RepositoryId = _0_IEV_PRO.EventMngrView._NP_RepositoryId


    _omni_op_d = {"notifyEvents": _0_IEV_PRO.EventMngrView._d_notifyEvents}
    _omni_op_d.update(_0_IBASE_IF__POA.View._omni_op_d)

EventMngrView._omni_skeleton = EventMngrView
_0_IEV_PRO__POA.EventMngrView = EventMngrView
omniORB.registerSkeleton(EventMngrView._NP_RepositoryId, EventMngrView)
del EventMngrView
__name__ = "IEV_PRO"

# interface EVserver
_0_IEV_PRO._d_EVserver = (omniORB.tcInternal.tv_objref, "IDL:IEV_PRO/EVserver:1.0", "EVserver")
omniORB.typeMapping["IDL:IEV_PRO/EVserver:1.0"] = _0_IEV_PRO._d_EVserver
_0_IEV_PRO.EVserver = omniORB.newEmptyClass()
class EVserver (_0_ICLOCK_PRO.TimingServer):
    _NP_RepositoryId = _0_IEV_PRO._d_EVserver[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_IEV_PRO.EVserver = EVserver
_0_IEV_PRO._tc_EVserver = omniORB.tcInternal.createTypeCode(_0_IEV_PRO._d_EVserver)
omniORB.registerType(EVserver._NP_RepositoryId, _0_IEV_PRO._d_EVserver, _0_IEV_PRO._tc_EVserver)

# EVserver operations and attributes
EVserver._d__get_m_eventMngr = ((),(omniORB.typeMapping["IDL:IEV_PRO/EventMngr:1.0"],),None)

# EVserver object reference
class _objref_EVserver (_0_ICLOCK_PRO._objref_TimingServer):
    _NP_RepositoryId = EVserver._NP_RepositoryId

    def __init__(self, obj):
        _0_ICLOCK_PRO._objref_TimingServer.__init__(self, obj)

    def _get_m_eventMngr(self, *args):
        return self._obj.invoke("_get_m_eventMngr", _0_IEV_PRO.EVserver._d__get_m_eventMngr, args)

    m_eventMngr = property(_get_m_eventMngr)


omniORB.registerObjref(EVserver._NP_RepositoryId, _objref_EVserver)
_0_IEV_PRO._objref_EVserver = _objref_EVserver
del EVserver, _objref_EVserver

# EVserver skeleton
__name__ = "IEV_PRO__POA"
class EVserver (_0_ICLOCK_PRO__POA.TimingServer):
    _NP_RepositoryId = _0_IEV_PRO.EVserver._NP_RepositoryId


    _omni_op_d = {"_get_m_eventMngr": _0_IEV_PRO.EVserver._d__get_m_eventMngr}
    _omni_op_d.update(_0_ICLOCK_PRO__POA.TimingServer._omni_op_d)

EVserver._omni_skeleton = EVserver
_0_IEV_PRO__POA.EVserver = EVserver
omniORB.registerSkeleton(EVserver._NP_RepositoryId, EVserver)
del EVserver
__name__ = "IEV_PRO"

# interface EVserverMngr
_0_IEV_PRO._d_EVserverMngr = (omniORB.tcInternal.tv_objref, "IDL:IEV_PRO/EVserverMngr:1.0", "EVserverMngr")
omniORB.typeMapping["IDL:IEV_PRO/EVserverMngr:1.0"] = _0_IEV_PRO._d_EVserverMngr
_0_IEV_PRO.EVserverMngr = omniORB.newEmptyClass()
class EVserverMngr (_0_ICLOCK_PRO.TimingServerMngr):
    _NP_RepositoryId = _0_IEV_PRO._d_EVserverMngr[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil

    ServiceName = "EV_PRO_001"


_0_IEV_PRO.EVserverMngr = EVserverMngr
_0_IEV_PRO._tc_EVserverMngr = omniORB.tcInternal.createTypeCode(_0_IEV_PRO._d_EVserverMngr)
omniORB.registerType(EVserverMngr._NP_RepositoryId, _0_IEV_PRO._d_EVserverMngr, _0_IEV_PRO._tc_EVserverMngr)

# EVserverMngr operations and attributes
EVserverMngr._d_getEVserver = ((omniORB.tcInternal.tv_boolean, ), (omniORB.typeMapping["IDL:IEV_PRO/EVserver:1.0"], ), {_0_IBASE.NotFound._NP_RepositoryId: _0_IBASE._d_NotFound})

# EVserverMngr object reference
class _objref_EVserverMngr (_0_ICLOCK_PRO._objref_TimingServerMngr):
    _NP_RepositoryId = EVserverMngr._NP_RepositoryId

    def __init__(self, obj):
        _0_ICLOCK_PRO._objref_TimingServerMngr.__init__(self, obj)

    def getEVserver(self, *args):
        return self._obj.invoke("getEVserver", _0_IEV_PRO.EVserverMngr._d_getEVserver, args)

omniORB.registerObjref(EVserverMngr._NP_RepositoryId, _objref_EVserverMngr)
_0_IEV_PRO._objref_EVserverMngr = _objref_EVserverMngr
del EVserverMngr, _objref_EVserverMngr

# EVserverMngr skeleton
__name__ = "IEV_PRO__POA"
class EVserverMngr (_0_ICLOCK_PRO__POA.TimingServerMngr):
    _NP_RepositoryId = _0_IEV_PRO.EVserverMngr._NP_RepositoryId


    _omni_op_d = {"getEVserver": _0_IEV_PRO.EVserverMngr._d_getEVserver}
    _omni_op_d.update(_0_ICLOCK_PRO__POA.TimingServerMngr._omni_op_d)

EVserverMngr._omni_skeleton = EVserverMngr
_0_IEV_PRO__POA.EVserverMngr = EVserverMngr
omniORB.registerSkeleton(EVserverMngr._NP_RepositoryId, EVserverMngr)
del EVserverMngr
__name__ = "IEV_PRO"

#
# End of module "IEV_PRO"
#
__name__ = "IEV_PRO_idl"

_exported_modules = ( "IEV_PRO", )

# The end.
