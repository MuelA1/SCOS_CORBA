# Python stubs generated by omniidl from ITMP_PRO.idl
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

# #include "ITMP.idl"
import ITMP_idl
_0_ITMP = omniORB.openModule("ITMP")
_0_ITMP__POA = omniORB.openModule("ITMP__POA")

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
# Start of module "ITMP_PRO"
#
__name__ = "ITMP_PRO"
_0_ITMP_PRO = omniORB.openModule("ITMP_PRO", r"ITMP_PRO.idl")
_0_ITMP_PRO__POA = omniORB.openModule("ITMP_PRO__POA", r"ITMP_PRO.idl")


# forward interface TMpacketMngrView;
_0_ITMP_PRO._d_TMpacketMngrView = (omniORB.tcInternal.tv_objref, "IDL:ITMP_PRO/TMpacketMngrView:1.0", "TMpacketMngrView")
omniORB.typeMapping["IDL:ITMP_PRO/TMpacketMngrView:1.0"] = _0_ITMP_PRO._d_TMpacketMngrView

# interface TMpacketMngr
_0_ITMP_PRO._d_TMpacketMngr = (omniORB.tcInternal.tv_objref, "IDL:ITMP_PRO/TMpacketMngr:1.0", "TMpacketMngr")
omniORB.typeMapping["IDL:ITMP_PRO/TMpacketMngr:1.0"] = _0_ITMP_PRO._d_TMpacketMngr
_0_ITMP_PRO.TMpacketMngr = omniORB.newEmptyClass()
class TMpacketMngr (_0_IBASE_IF.Model):
    _NP_RepositoryId = _0_ITMP_PRO._d_TMpacketMngr[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_ITMP_PRO.TMpacketMngr = TMpacketMngr
_0_ITMP_PRO._tc_TMpacketMngr = omniORB.tcInternal.createTypeCode(_0_ITMP_PRO._d_TMpacketMngr)
omniORB.registerType(TMpacketMngr._NP_RepositoryId, _0_ITMP_PRO._d_TMpacketMngr, _0_ITMP_PRO._tc_TMpacketMngr)

# TMpacketMngr operations and attributes
TMpacketMngr._d_registerTMpackets = ((omniORB.typeMapping["IDL:ITMP_PRO/TMpacketMngrView:1.0"], omniORB.typeMapping["IDL:ITMP/TMpacketFilter:1.0"], omniORB.typeMapping["IDL:ITMP/TransmissionFilter:1.0"]), (omniORB.tcInternal.tv_long, ), None)
TMpacketMngr._d_unregisterTMpackets = ((omniORB.tcInternal.tv_long, ), (omniORB.tcInternal.tv_boolean, ), None)
TMpacketMngr._d_modifyTMpacketFilter = ((omniORB.tcInternal.tv_long, omniORB.typeMapping["IDL:ITMP/TMpacketFilter:1.0"]), (omniORB.tcInternal.tv_boolean, ), None)
TMpacketMngr._d_modifyTransmissionFilter = ((omniORB.tcInternal.tv_long, omniORB.typeMapping["IDL:ITMP/TransmissionFilter:1.0"]), (omniORB.tcInternal.tv_boolean, ), None)
TMpacketMngr._d_getFullData = ((omniORB.tcInternal.tv_long, ), (omniORB.typeMapping["IDL:ITMP/TMpacketNotifyDatas:1.0"], ), {_0_ICLOCK.NotPossible._NP_RepositoryId: _0_ICLOCK._d_NotPossible})
TMpacketMngr._d_getNextData = ((omniORB.tcInternal.tv_long, ), (omniORB.typeMapping["IDL:ITMP/TMpacketNotifyDatas:1.0"], ), {_0_ICLOCK.NotPossible._NP_RepositoryId: _0_ICLOCK._d_NotPossible})

# TMpacketMngr object reference
class _objref_TMpacketMngr (_0_IBASE_IF._objref_Model):
    _NP_RepositoryId = TMpacketMngr._NP_RepositoryId

    def __init__(self, obj):
        _0_IBASE_IF._objref_Model.__init__(self, obj)

    def registerTMpackets(self, *args):
        return self._obj.invoke("registerTMpackets", _0_ITMP_PRO.TMpacketMngr._d_registerTMpackets, args)

    def unregisterTMpackets(self, *args):
        return self._obj.invoke("unregisterTMpackets", _0_ITMP_PRO.TMpacketMngr._d_unregisterTMpackets, args)

    def modifyTMpacketFilter(self, *args):
        return self._obj.invoke("modifyTMpacketFilter", _0_ITMP_PRO.TMpacketMngr._d_modifyTMpacketFilter, args)

    def modifyTransmissionFilter(self, *args):
        return self._obj.invoke("modifyTransmissionFilter", _0_ITMP_PRO.TMpacketMngr._d_modifyTransmissionFilter, args)

    def getFullData(self, *args):
        return self._obj.invoke("getFullData", _0_ITMP_PRO.TMpacketMngr._d_getFullData, args)

    def getNextData(self, *args):
        return self._obj.invoke("getNextData", _0_ITMP_PRO.TMpacketMngr._d_getNextData, args)

omniORB.registerObjref(TMpacketMngr._NP_RepositoryId, _objref_TMpacketMngr)
_0_ITMP_PRO._objref_TMpacketMngr = _objref_TMpacketMngr
del TMpacketMngr, _objref_TMpacketMngr

# TMpacketMngr skeleton
__name__ = "ITMP_PRO__POA"
class TMpacketMngr (_0_IBASE_IF__POA.Model):
    _NP_RepositoryId = _0_ITMP_PRO.TMpacketMngr._NP_RepositoryId


    _omni_op_d = {"registerTMpackets": _0_ITMP_PRO.TMpacketMngr._d_registerTMpackets, "unregisterTMpackets": _0_ITMP_PRO.TMpacketMngr._d_unregisterTMpackets, "modifyTMpacketFilter": _0_ITMP_PRO.TMpacketMngr._d_modifyTMpacketFilter, "modifyTransmissionFilter": _0_ITMP_PRO.TMpacketMngr._d_modifyTransmissionFilter, "getFullData": _0_ITMP_PRO.TMpacketMngr._d_getFullData, "getNextData": _0_ITMP_PRO.TMpacketMngr._d_getNextData}
    _omni_op_d.update(_0_IBASE_IF__POA.Model._omni_op_d)

TMpacketMngr._omni_skeleton = TMpacketMngr
_0_ITMP_PRO__POA.TMpacketMngr = TMpacketMngr
omniORB.registerSkeleton(TMpacketMngr._NP_RepositoryId, TMpacketMngr)
del TMpacketMngr
__name__ = "ITMP_PRO"

# interface TMpacketMngrView
_0_ITMP_PRO._d_TMpacketMngrView = (omniORB.tcInternal.tv_objref, "IDL:ITMP_PRO/TMpacketMngrView:1.0", "TMpacketMngrView")
omniORB.typeMapping["IDL:ITMP_PRO/TMpacketMngrView:1.0"] = _0_ITMP_PRO._d_TMpacketMngrView
_0_ITMP_PRO.TMpacketMngrView = omniORB.newEmptyClass()
class TMpacketMngrView (_0_IBASE_IF.View):
    _NP_RepositoryId = _0_ITMP_PRO._d_TMpacketMngrView[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_ITMP_PRO.TMpacketMngrView = TMpacketMngrView
_0_ITMP_PRO._tc_TMpacketMngrView = omniORB.tcInternal.createTypeCode(_0_ITMP_PRO._d_TMpacketMngrView)
omniORB.registerType(TMpacketMngrView._NP_RepositoryId, _0_ITMP_PRO._d_TMpacketMngrView, _0_ITMP_PRO._tc_TMpacketMngrView)

# TMpacketMngrView operations and attributes
TMpacketMngrView._d_notifyTMpackets = ((omniORB.typeMapping["IDL:ITMP/TMpacketNotifyDatas:1.0"], ), (), None)

# TMpacketMngrView object reference
class _objref_TMpacketMngrView (_0_IBASE_IF._objref_View):
    _NP_RepositoryId = TMpacketMngrView._NP_RepositoryId

    def __init__(self, obj):
        _0_IBASE_IF._objref_View.__init__(self, obj)

    def notifyTMpackets(self, *args):
        return self._obj.invoke("notifyTMpackets", _0_ITMP_PRO.TMpacketMngrView._d_notifyTMpackets, args)

omniORB.registerObjref(TMpacketMngrView._NP_RepositoryId, _objref_TMpacketMngrView)
_0_ITMP_PRO._objref_TMpacketMngrView = _objref_TMpacketMngrView
del TMpacketMngrView, _objref_TMpacketMngrView

# TMpacketMngrView skeleton
__name__ = "ITMP_PRO__POA"
class TMpacketMngrView (_0_IBASE_IF__POA.View):
    _NP_RepositoryId = _0_ITMP_PRO.TMpacketMngrView._NP_RepositoryId


    _omni_op_d = {"notifyTMpackets": _0_ITMP_PRO.TMpacketMngrView._d_notifyTMpackets}
    _omni_op_d.update(_0_IBASE_IF__POA.View._omni_op_d)

TMpacketMngrView._omni_skeleton = TMpacketMngrView
_0_ITMP_PRO__POA.TMpacketMngrView = TMpacketMngrView
omniORB.registerSkeleton(TMpacketMngrView._NP_RepositoryId, TMpacketMngrView)
del TMpacketMngrView
__name__ = "ITMP_PRO"

# interface TMPserver
_0_ITMP_PRO._d_TMPserver = (omniORB.tcInternal.tv_objref, "IDL:ITMP_PRO/TMPserver:1.0", "TMPserver")
omniORB.typeMapping["IDL:ITMP_PRO/TMPserver:1.0"] = _0_ITMP_PRO._d_TMPserver
_0_ITMP_PRO.TMPserver = omniORB.newEmptyClass()
class TMPserver (_0_ICLOCK_PRO.TimingServer):
    _NP_RepositoryId = _0_ITMP_PRO._d_TMPserver[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_ITMP_PRO.TMPserver = TMPserver
_0_ITMP_PRO._tc_TMPserver = omniORB.tcInternal.createTypeCode(_0_ITMP_PRO._d_TMPserver)
omniORB.registerType(TMPserver._NP_RepositoryId, _0_ITMP_PRO._d_TMPserver, _0_ITMP_PRO._tc_TMPserver)

# TMPserver operations and attributes
TMPserver._d__get_m_packetMngr = ((),(omniORB.typeMapping["IDL:ITMP_PRO/TMpacketMngr:1.0"],),None)

# TMPserver object reference
class _objref_TMPserver (_0_ICLOCK_PRO._objref_TimingServer):
    _NP_RepositoryId = TMPserver._NP_RepositoryId

    def __init__(self, obj):
        _0_ICLOCK_PRO._objref_TimingServer.__init__(self, obj)

    def _get_m_packetMngr(self, *args):
        return self._obj.invoke("_get_m_packetMngr", _0_ITMP_PRO.TMPserver._d__get_m_packetMngr, args)

    m_packetMngr = property(_get_m_packetMngr)


omniORB.registerObjref(TMPserver._NP_RepositoryId, _objref_TMPserver)
_0_ITMP_PRO._objref_TMPserver = _objref_TMPserver
del TMPserver, _objref_TMPserver

# TMPserver skeleton
__name__ = "ITMP_PRO__POA"
class TMPserver (_0_ICLOCK_PRO__POA.TimingServer):
    _NP_RepositoryId = _0_ITMP_PRO.TMPserver._NP_RepositoryId


    _omni_op_d = {"_get_m_packetMngr": _0_ITMP_PRO.TMPserver._d__get_m_packetMngr}
    _omni_op_d.update(_0_ICLOCK_PRO__POA.TimingServer._omni_op_d)

TMPserver._omni_skeleton = TMPserver
_0_ITMP_PRO__POA.TMPserver = TMPserver
omniORB.registerSkeleton(TMPserver._NP_RepositoryId, TMPserver)
del TMPserver
__name__ = "ITMP_PRO"

# interface TMPserverMngr
_0_ITMP_PRO._d_TMPserverMngr = (omniORB.tcInternal.tv_objref, "IDL:ITMP_PRO/TMPserverMngr:1.0", "TMPserverMngr")
omniORB.typeMapping["IDL:ITMP_PRO/TMPserverMngr:1.0"] = _0_ITMP_PRO._d_TMPserverMngr
_0_ITMP_PRO.TMPserverMngr = omniORB.newEmptyClass()
class TMPserverMngr (_0_ICLOCK_PRO.TimingServerMngr):
    _NP_RepositoryId = _0_ITMP_PRO._d_TMPserverMngr[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil

    ServiceName = "TMP_PRO_001"


_0_ITMP_PRO.TMPserverMngr = TMPserverMngr
_0_ITMP_PRO._tc_TMPserverMngr = omniORB.tcInternal.createTypeCode(_0_ITMP_PRO._d_TMPserverMngr)
omniORB.registerType(TMPserverMngr._NP_RepositoryId, _0_ITMP_PRO._d_TMPserverMngr, _0_ITMP_PRO._tc_TMPserverMngr)

# TMPserverMngr operations and attributes
TMPserverMngr._d_getTMPserver = ((omniORB.tcInternal.tv_boolean, ), (omniORB.typeMapping["IDL:ITMP_PRO/TMPserver:1.0"], ), {_0_IBASE.NotFound._NP_RepositoryId: _0_IBASE._d_NotFound})

# TMPserverMngr object reference
class _objref_TMPserverMngr (_0_ICLOCK_PRO._objref_TimingServerMngr):
    _NP_RepositoryId = TMPserverMngr._NP_RepositoryId

    def __init__(self, obj):
        _0_ICLOCK_PRO._objref_TimingServerMngr.__init__(self, obj)

    def getTMPserver(self, *args):
        return self._obj.invoke("getTMPserver", _0_ITMP_PRO.TMPserverMngr._d_getTMPserver, args)

omniORB.registerObjref(TMPserverMngr._NP_RepositoryId, _objref_TMPserverMngr)
_0_ITMP_PRO._objref_TMPserverMngr = _objref_TMPserverMngr
del TMPserverMngr, _objref_TMPserverMngr

# TMPserverMngr skeleton
__name__ = "ITMP_PRO__POA"
class TMPserverMngr (_0_ICLOCK_PRO__POA.TimingServerMngr):
    _NP_RepositoryId = _0_ITMP_PRO.TMPserverMngr._NP_RepositoryId


    _omni_op_d = {"getTMPserver": _0_ITMP_PRO.TMPserverMngr._d_getTMPserver}
    _omni_op_d.update(_0_ICLOCK_PRO__POA.TimingServerMngr._omni_op_d)

TMPserverMngr._omni_skeleton = TMPserverMngr
_0_ITMP_PRO__POA.TMPserverMngr = TMPserverMngr
omniORB.registerSkeleton(TMPserverMngr._NP_RepositoryId, TMPserverMngr)
del TMPserverMngr
__name__ = "ITMP_PRO"

# interface TMPhistoryQueryMngr
_0_ITMP_PRO._d_TMPhistoryQueryMngr = (omniORB.tcInternal.tv_objref, "IDL:ITMP_PRO/TMPhistoryQueryMngr:1.0", "TMPhistoryQueryMngr")
omniORB.typeMapping["IDL:ITMP_PRO/TMPhistoryQueryMngr:1.0"] = _0_ITMP_PRO._d_TMPhistoryQueryMngr
_0_ITMP_PRO.TMPhistoryQueryMngr = omniORB.newEmptyClass()
class TMPhistoryQueryMngr :
    _NP_RepositoryId = _0_ITMP_PRO._d_TMPhistoryQueryMngr[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil

    ServiceName = "TMPQ_PRO_001"


_0_ITMP_PRO.TMPhistoryQueryMngr = TMPhistoryQueryMngr
_0_ITMP_PRO._tc_TMPhistoryQueryMngr = omniORB.tcInternal.createTypeCode(_0_ITMP_PRO._d_TMPhistoryQueryMngr)
omniORB.registerType(TMPhistoryQueryMngr._NP_RepositoryId, _0_ITMP_PRO._d_TMPhistoryQueryMngr, _0_ITMP_PRO._tc_TMPhistoryQueryMngr)

# TMPhistoryQueryMngr operations and attributes
TMPhistoryQueryMngr._d_getHistoryData = ((omniORB.tcInternal.tv_ulong, omniORB.tcInternal.tv_ushort, omniORB.typeMapping["IDL:IBASE/Time:1.0"], omniORB.typeMapping["IDL:IBASE/Time:1.0"]), (omniORB.typeMapping["IDL:ITMP/TMpacketNotifyData:1.0"], ), {_0_ICLOCK.NotPossible._NP_RepositoryId: _0_ICLOCK._d_NotPossible})

# TMPhistoryQueryMngr object reference
class _objref_TMPhistoryQueryMngr (CORBA.Object):
    _NP_RepositoryId = TMPhistoryQueryMngr._NP_RepositoryId

    def __init__(self, obj):
        CORBA.Object.__init__(self, obj)

    def getHistoryData(self, *args):
        return self._obj.invoke("getHistoryData", _0_ITMP_PRO.TMPhistoryQueryMngr._d_getHistoryData, args)

omniORB.registerObjref(TMPhistoryQueryMngr._NP_RepositoryId, _objref_TMPhistoryQueryMngr)
_0_ITMP_PRO._objref_TMPhistoryQueryMngr = _objref_TMPhistoryQueryMngr
del TMPhistoryQueryMngr, _objref_TMPhistoryQueryMngr

# TMPhistoryQueryMngr skeleton
__name__ = "ITMP_PRO__POA"
class TMPhistoryQueryMngr (PortableServer.Servant):
    _NP_RepositoryId = _0_ITMP_PRO.TMPhistoryQueryMngr._NP_RepositoryId


    _omni_op_d = {"getHistoryData": _0_ITMP_PRO.TMPhistoryQueryMngr._d_getHistoryData}

TMPhistoryQueryMngr._omni_skeleton = TMPhistoryQueryMngr
_0_ITMP_PRO__POA.TMPhistoryQueryMngr = TMPhistoryQueryMngr
omniORB.registerSkeleton(TMPhistoryQueryMngr._NP_RepositoryId, TMPhistoryQueryMngr)
del TMPhistoryQueryMngr
__name__ = "ITMP_PRO"

#
# End of module "ITMP_PRO"
#
__name__ = "ITMP_PRO_idl"

_exported_modules = ( "ITMP_PRO", )

# The end.
