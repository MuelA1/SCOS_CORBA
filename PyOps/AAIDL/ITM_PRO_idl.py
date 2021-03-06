# Python stubs generated by omniidl from ITM_PRO.idl
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

# #include "IMIB.idl"
import IMIB_idl
_0_IMIB = omniORB.openModule("IMIB")
_0_IMIB__POA = omniORB.openModule("IMIB__POA")

# #include "ITMSET.idl"
import ITMSET_idl
_0_ITMSET = omniORB.openModule("ITMSET")
_0_ITMSET__POA = omniORB.openModule("ITMSET__POA")

# #include "ITMSET_PRO.idl"
import ITMSET_PRO_idl
_0_ITMSET_PRO = omniORB.openModule("ITMSET_PRO")
_0_ITMSET_PRO__POA = omniORB.openModule("ITMSET_PRO__POA")

#
# Start of module "ITM_PRO"
#
__name__ = "ITM_PRO"
_0_ITM_PRO = omniORB.openModule("ITM_PRO", r"ITM_PRO.idl")
_0_ITM_PRO__POA = omniORB.openModule("ITM_PRO__POA", r"ITM_PRO.idl")


# forward interface ParameterView;
_0_ITM_PRO._d_ParameterView = (omniORB.tcInternal.tv_objref, "IDL:ITM_PRO/ParameterView:1.0", "ParameterView")
omniORB.typeMapping["IDL:ITM_PRO/ParameterView:1.0"] = _0_ITM_PRO._d_ParameterView

# struct RegParamInit
_0_ITM_PRO.RegParamInit = omniORB.newEmptyClass()
class RegParamInit (omniORB.StructBase):
    _NP_RepositoryId = "IDL:ITM_PRO/RegParamInit:1.0"

    def __init__(self, m_key, m_initValue):
        self.m_key = m_key
        self.m_initValue = m_initValue

_0_ITM_PRO.RegParamInit = RegParamInit
_0_ITM_PRO._d_RegParamInit  = (omniORB.tcInternal.tv_struct, RegParamInit, RegParamInit._NP_RepositoryId, "RegParamInit", "m_key", omniORB.tcInternal.tv_long, "m_initValue", omniORB.typeMapping["IDL:ITM/AllValues:1.0"])
_0_ITM_PRO._tc_RegParamInit = omniORB.tcInternal.createTypeCode(_0_ITM_PRO._d_RegParamInit)
omniORB.registerType(RegParamInit._NP_RepositoryId, _0_ITM_PRO._d_RegParamInit, _0_ITM_PRO._tc_RegParamInit)
del RegParamInit

# interface Parameter
_0_ITM_PRO._d_Parameter = (omniORB.tcInternal.tv_objref, "IDL:ITM_PRO/Parameter:1.0", "Parameter")
omniORB.typeMapping["IDL:ITM_PRO/Parameter:1.0"] = _0_ITM_PRO._d_Parameter
_0_ITM_PRO.Parameter = omniORB.newEmptyClass()
class Parameter (_0_IBASE_IF.Model):
    _NP_RepositoryId = _0_ITM_PRO._d_Parameter[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_ITM_PRO.Parameter = Parameter
_0_ITM_PRO._tc_Parameter = omniORB.tcInternal.createTypeCode(_0_ITM_PRO._d_Parameter)
omniORB.registerType(Parameter._NP_RepositoryId, _0_ITM_PRO._d_Parameter, _0_ITM_PRO._tc_Parameter)

# Parameter operations and attributes
Parameter._d__get_m_definition = ((),(omniORB.typeMapping["IDL:IMIB/ParamDef:1.0"],),None)
Parameter._d_getChangedAttribute = ((), (omniORB.typeMapping["IDL:IMIB/ParamAttributeType:1.0"], ), None)
Parameter._d_getRawValue = ((), (omniORB.typeMapping["IDL:ITM/Value:1.0"], ), {_0_IBASE.NotFound._NP_RepositoryId: _0_IBASE._d_NotFound})
Parameter._d_getEngValue = ((), (omniORB.typeMapping["IDL:ITM/Value:1.0"], ), {_0_IBASE.NotFound._NP_RepositoryId: _0_IBASE._d_NotFound})
Parameter._d_getSynValue = ((), (omniORB.typeMapping["IDL:ITM/Value:1.0"], ), {_0_IBASE.NotFound._NP_RepositoryId: _0_IBASE._d_NotFound})
Parameter._d_getSourceValue = ((), (omniORB.typeMapping["IDL:ITM/Value:1.0"], ), {_0_IBASE.NotFound._NP_RepositoryId: _0_IBASE._d_NotFound})
Parameter._d_getDefaultValue = ((), (omniORB.typeMapping["IDL:ITM/Value:1.0"], ), {_0_IBASE.NotFound._NP_RepositoryId: _0_IBASE._d_NotFound})
Parameter._d_allValuesValid = ((), (omniORB.tcInternal.tv_boolean, ), None)
Parameter._d_getOOLstate = ((), (omniORB.typeMapping["IDL:ITM/OOLstate:1.0"], ), None)
Parameter._d_getActualLowLimit = ((), (omniORB.typeMapping["IDL:IBASE/Variant:1.0"], ), None)
Parameter._d_getActualHighLimit = ((), (omniORB.typeMapping["IDL:IBASE/Variant:1.0"], ), None)
Parameter._d_getSCCstate = ((), (omniORB.typeMapping["IDL:ITM/SCCstate:1.0"], ), None)
Parameter._d_registerParam = ((omniORB.typeMapping["IDL:ITM_PRO/ParameterView:1.0"], omniORB.tcInternal.tv_boolean, omniORB.typeMapping["IDL:IMIB/ParamValueType:1.0"], omniORB.tcInternal.tv_boolean), (omniORB.tcInternal.tv_long, ), None)
Parameter._d_registerParamInit = ((omniORB.typeMapping["IDL:ITM_PRO/ParameterView:1.0"], omniORB.tcInternal.tv_boolean, omniORB.typeMapping["IDL:IMIB/ParamValueType:1.0"], omniORB.tcInternal.tv_boolean), (omniORB.typeMapping["IDL:ITM_PRO/RegParamInit:1.0"], ), None)
Parameter._d_getFullData = ((omniORB.tcInternal.tv_long, ), (omniORB.typeMapping["IDL:ITM/AllValues:1.0"], ), None)

# Parameter object reference
class _objref_Parameter (_0_IBASE_IF._objref_Model):
    _NP_RepositoryId = Parameter._NP_RepositoryId

    def __init__(self, obj):
        _0_IBASE_IF._objref_Model.__init__(self, obj)

    def _get_m_definition(self, *args):
        return self._obj.invoke("_get_m_definition", _0_ITM_PRO.Parameter._d__get_m_definition, args)

    m_definition = property(_get_m_definition)


    def getChangedAttribute(self, *args):
        return self._obj.invoke("getChangedAttribute", _0_ITM_PRO.Parameter._d_getChangedAttribute, args)

    def getRawValue(self, *args):
        return self._obj.invoke("getRawValue", _0_ITM_PRO.Parameter._d_getRawValue, args)

    def getEngValue(self, *args):
        return self._obj.invoke("getEngValue", _0_ITM_PRO.Parameter._d_getEngValue, args)

    def getSynValue(self, *args):
        return self._obj.invoke("getSynValue", _0_ITM_PRO.Parameter._d_getSynValue, args)

    def getSourceValue(self, *args):
        return self._obj.invoke("getSourceValue", _0_ITM_PRO.Parameter._d_getSourceValue, args)

    def getDefaultValue(self, *args):
        return self._obj.invoke("getDefaultValue", _0_ITM_PRO.Parameter._d_getDefaultValue, args)

    def allValuesValid(self, *args):
        return self._obj.invoke("allValuesValid", _0_ITM_PRO.Parameter._d_allValuesValid, args)

    def getOOLstate(self, *args):
        return self._obj.invoke("getOOLstate", _0_ITM_PRO.Parameter._d_getOOLstate, args)

    def getActualLowLimit(self, *args):
        return self._obj.invoke("getActualLowLimit", _0_ITM_PRO.Parameter._d_getActualLowLimit, args)

    def getActualHighLimit(self, *args):
        return self._obj.invoke("getActualHighLimit", _0_ITM_PRO.Parameter._d_getActualHighLimit, args)

    def getSCCstate(self, *args):
        return self._obj.invoke("getSCCstate", _0_ITM_PRO.Parameter._d_getSCCstate, args)

    def registerParam(self, *args):
        return self._obj.invoke("registerParam", _0_ITM_PRO.Parameter._d_registerParam, args)

    def registerParamInit(self, *args):
        return self._obj.invoke("registerParamInit", _0_ITM_PRO.Parameter._d_registerParamInit, args)

    def getFullData(self, *args):
        return self._obj.invoke("getFullData", _0_ITM_PRO.Parameter._d_getFullData, args)

omniORB.registerObjref(Parameter._NP_RepositoryId, _objref_Parameter)
_0_ITM_PRO._objref_Parameter = _objref_Parameter
del Parameter, _objref_Parameter

# Parameter skeleton
__name__ = "ITM_PRO__POA"
class Parameter (_0_IBASE_IF__POA.Model):
    _NP_RepositoryId = _0_ITM_PRO.Parameter._NP_RepositoryId


    _omni_op_d = {"_get_m_definition": _0_ITM_PRO.Parameter._d__get_m_definition, "getChangedAttribute": _0_ITM_PRO.Parameter._d_getChangedAttribute, "getRawValue": _0_ITM_PRO.Parameter._d_getRawValue, "getEngValue": _0_ITM_PRO.Parameter._d_getEngValue, "getSynValue": _0_ITM_PRO.Parameter._d_getSynValue, "getSourceValue": _0_ITM_PRO.Parameter._d_getSourceValue, "getDefaultValue": _0_ITM_PRO.Parameter._d_getDefaultValue, "allValuesValid": _0_ITM_PRO.Parameter._d_allValuesValid, "getOOLstate": _0_ITM_PRO.Parameter._d_getOOLstate, "getActualLowLimit": _0_ITM_PRO.Parameter._d_getActualLowLimit, "getActualHighLimit": _0_ITM_PRO.Parameter._d_getActualHighLimit, "getSCCstate": _0_ITM_PRO.Parameter._d_getSCCstate, "registerParam": _0_ITM_PRO.Parameter._d_registerParam, "registerParamInit": _0_ITM_PRO.Parameter._d_registerParamInit, "getFullData": _0_ITM_PRO.Parameter._d_getFullData}
    _omni_op_d.update(_0_IBASE_IF__POA.Model._omni_op_d)

Parameter._omni_skeleton = Parameter
_0_ITM_PRO__POA.Parameter = Parameter
omniORB.registerSkeleton(Parameter._NP_RepositoryId, Parameter)
del Parameter
__name__ = "ITM_PRO"

# interface ParameterView
_0_ITM_PRO._d_ParameterView = (omniORB.tcInternal.tv_objref, "IDL:ITM_PRO/ParameterView:1.0", "ParameterView")
omniORB.typeMapping["IDL:ITM_PRO/ParameterView:1.0"] = _0_ITM_PRO._d_ParameterView
_0_ITM_PRO.ParameterView = omniORB.newEmptyClass()
class ParameterView (_0_IBASE_IF.View):
    _NP_RepositoryId = _0_ITM_PRO._d_ParameterView[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_ITM_PRO.ParameterView = ParameterView
_0_ITM_PRO._tc_ParameterView = omniORB.tcInternal.createTypeCode(_0_ITM_PRO._d_ParameterView)
omniORB.registerType(ParameterView._NP_RepositoryId, _0_ITM_PRO._d_ParameterView, _0_ITM_PRO._tc_ParameterView)

# ParameterView operations and attributes
ParameterView._d_notifyParameter = ((omniORB.tcInternal.tv_long, omniORB.typeMapping["IDL:ITM/AllValues:1.0"]), (), None)

# ParameterView object reference
class _objref_ParameterView (_0_IBASE_IF._objref_View):
    _NP_RepositoryId = ParameterView._NP_RepositoryId

    def __init__(self, obj):
        _0_IBASE_IF._objref_View.__init__(self, obj)

    def notifyParameter(self, *args):
        return self._obj.invoke("notifyParameter", _0_ITM_PRO.ParameterView._d_notifyParameter, args)

omniORB.registerObjref(ParameterView._NP_RepositoryId, _objref_ParameterView)
_0_ITM_PRO._objref_ParameterView = _objref_ParameterView
del ParameterView, _objref_ParameterView

# ParameterView skeleton
__name__ = "ITM_PRO__POA"
class ParameterView (_0_IBASE_IF__POA.View):
    _NP_RepositoryId = _0_ITM_PRO.ParameterView._NP_RepositoryId


    _omni_op_d = {"notifyParameter": _0_ITM_PRO.ParameterView._d_notifyParameter}
    _omni_op_d.update(_0_IBASE_IF__POA.View._omni_op_d)

ParameterView._omni_skeleton = ParameterView
_0_ITM_PRO__POA.ParameterView = ParameterView
omniORB.registerSkeleton(ParameterView._NP_RepositoryId, ParameterView)
del ParameterView
__name__ = "ITM_PRO"

# interface ParameterMngr
_0_ITM_PRO._d_ParameterMngr = (omniORB.tcInternal.tv_objref, "IDL:ITM_PRO/ParameterMngr:1.0", "ParameterMngr")
omniORB.typeMapping["IDL:ITM_PRO/ParameterMngr:1.0"] = _0_ITM_PRO._d_ParameterMngr
_0_ITM_PRO.ParameterMngr = omniORB.newEmptyClass()
class ParameterMngr :
    _NP_RepositoryId = _0_ITM_PRO._d_ParameterMngr[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_ITM_PRO.ParameterMngr = ParameterMngr
_0_ITM_PRO._tc_ParameterMngr = omniORB.tcInternal.createTypeCode(_0_ITM_PRO._d_ParameterMngr)
omniORB.registerType(ParameterMngr._NP_RepositoryId, _0_ITM_PRO._d_ParameterMngr, _0_ITM_PRO._tc_ParameterMngr)

# ParameterMngr operations and attributes
ParameterMngr._d_getParameter = (((omniORB.tcInternal.tv_string,0), omniORB.typeMapping["IDL:omg.org/CORBA/Object:1.0"]), (omniORB.typeMapping["IDL:ITM_PRO/Parameter:1.0"], ), {_0_IBASE.NotFound._NP_RepositoryId: _0_IBASE._d_NotFound})

# ParameterMngr object reference
class _objref_ParameterMngr (CORBA.Object):
    _NP_RepositoryId = ParameterMngr._NP_RepositoryId

    def __init__(self, obj):
        CORBA.Object.__init__(self, obj)

    def getParameter(self, *args):
        return self._obj.invoke("getParameter", _0_ITM_PRO.ParameterMngr._d_getParameter, args)

omniORB.registerObjref(ParameterMngr._NP_RepositoryId, _objref_ParameterMngr)
_0_ITM_PRO._objref_ParameterMngr = _objref_ParameterMngr
del ParameterMngr, _objref_ParameterMngr

# ParameterMngr skeleton
__name__ = "ITM_PRO__POA"
class ParameterMngr (PortableServer.Servant):
    _NP_RepositoryId = _0_ITM_PRO.ParameterMngr._NP_RepositoryId


    _omni_op_d = {"getParameter": _0_ITM_PRO.ParameterMngr._d_getParameter}

ParameterMngr._omni_skeleton = ParameterMngr
_0_ITM_PRO__POA.ParameterMngr = ParameterMngr
omniORB.registerSkeleton(ParameterMngr._NP_RepositoryId, ParameterMngr)
del ParameterMngr
__name__ = "ITM_PRO"

# interface TMserver
_0_ITM_PRO._d_TMserver = (omniORB.tcInternal.tv_objref, "IDL:ITM_PRO/TMserver:1.0", "TMserver")
omniORB.typeMapping["IDL:ITM_PRO/TMserver:1.0"] = _0_ITM_PRO._d_TMserver
_0_ITM_PRO.TMserver = omniORB.newEmptyClass()
class TMserver (_0_ICLOCK_PRO.TimingServer):
    _NP_RepositoryId = _0_ITM_PRO._d_TMserver[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_ITM_PRO.TMserver = TMserver
_0_ITM_PRO._tc_TMserver = omniORB.tcInternal.createTypeCode(_0_ITM_PRO._d_TMserver)
omniORB.registerType(TMserver._NP_RepositoryId, _0_ITM_PRO._d_TMserver, _0_ITM_PRO._tc_TMserver)

# TMserver operations and attributes
TMserver._d__get_m_parameterMngr = ((),(omniORB.typeMapping["IDL:ITM_PRO/ParameterMngr:1.0"],),None)
TMserver._d__get_m_setMngr = ((),(omniORB.typeMapping["IDL:ITMSET_PRO/SetMngr:1.0"],),None)

# TMserver object reference
class _objref_TMserver (_0_ICLOCK_PRO._objref_TimingServer):
    _NP_RepositoryId = TMserver._NP_RepositoryId

    def __init__(self, obj):
        _0_ICLOCK_PRO._objref_TimingServer.__init__(self, obj)

    def _get_m_parameterMngr(self, *args):
        return self._obj.invoke("_get_m_parameterMngr", _0_ITM_PRO.TMserver._d__get_m_parameterMngr, args)

    m_parameterMngr = property(_get_m_parameterMngr)


    def _get_m_setMngr(self, *args):
        return self._obj.invoke("_get_m_setMngr", _0_ITM_PRO.TMserver._d__get_m_setMngr, args)

    m_setMngr = property(_get_m_setMngr)


omniORB.registerObjref(TMserver._NP_RepositoryId, _objref_TMserver)
_0_ITM_PRO._objref_TMserver = _objref_TMserver
del TMserver, _objref_TMserver

# TMserver skeleton
__name__ = "ITM_PRO__POA"
class TMserver (_0_ICLOCK_PRO__POA.TimingServer):
    _NP_RepositoryId = _0_ITM_PRO.TMserver._NP_RepositoryId


    _omni_op_d = {"_get_m_parameterMngr": _0_ITM_PRO.TMserver._d__get_m_parameterMngr, "_get_m_setMngr": _0_ITM_PRO.TMserver._d__get_m_setMngr}
    _omni_op_d.update(_0_ICLOCK_PRO__POA.TimingServer._omni_op_d)

TMserver._omni_skeleton = TMserver
_0_ITM_PRO__POA.TMserver = TMserver
omniORB.registerSkeleton(TMserver._NP_RepositoryId, TMserver)
del TMserver
__name__ = "ITM_PRO"

# interface TMserverMngr
_0_ITM_PRO._d_TMserverMngr = (omniORB.tcInternal.tv_objref, "IDL:ITM_PRO/TMserverMngr:1.0", "TMserverMngr")
omniORB.typeMapping["IDL:ITM_PRO/TMserverMngr:1.0"] = _0_ITM_PRO._d_TMserverMngr
_0_ITM_PRO.TMserverMngr = omniORB.newEmptyClass()
class TMserverMngr (_0_ICLOCK_PRO.TimingServerMngr):
    _NP_RepositoryId = _0_ITM_PRO._d_TMserverMngr[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil

    ServiceName = "TM_PRO_001"


_0_ITM_PRO.TMserverMngr = TMserverMngr
_0_ITM_PRO._tc_TMserverMngr = omniORB.tcInternal.createTypeCode(_0_ITM_PRO._d_TMserverMngr)
omniORB.registerType(TMserverMngr._NP_RepositoryId, _0_ITM_PRO._d_TMserverMngr, _0_ITM_PRO._tc_TMserverMngr)

# TMserverMngr operations and attributes
TMserverMngr._d_getTMserver = ((omniORB.tcInternal.tv_boolean, ), (omniORB.typeMapping["IDL:ITM_PRO/TMserver:1.0"], ), {_0_IBASE.NotFound._NP_RepositoryId: _0_IBASE._d_NotFound})

# TMserverMngr object reference
class _objref_TMserverMngr (_0_ICLOCK_PRO._objref_TimingServerMngr):
    _NP_RepositoryId = TMserverMngr._NP_RepositoryId

    def __init__(self, obj):
        _0_ICLOCK_PRO._objref_TimingServerMngr.__init__(self, obj)

    def getTMserver(self, *args):
        return self._obj.invoke("getTMserver", _0_ITM_PRO.TMserverMngr._d_getTMserver, args)

omniORB.registerObjref(TMserverMngr._NP_RepositoryId, _objref_TMserverMngr)
_0_ITM_PRO._objref_TMserverMngr = _objref_TMserverMngr
del TMserverMngr, _objref_TMserverMngr

# TMserverMngr skeleton
__name__ = "ITM_PRO__POA"
class TMserverMngr (_0_ICLOCK_PRO__POA.TimingServerMngr):
    _NP_RepositoryId = _0_ITM_PRO.TMserverMngr._NP_RepositoryId


    _omni_op_d = {"getTMserver": _0_ITM_PRO.TMserverMngr._d_getTMserver}
    _omni_op_d.update(_0_ICLOCK_PRO__POA.TimingServerMngr._omni_op_d)

TMserverMngr._omni_skeleton = TMserverMngr
_0_ITM_PRO__POA.TMserverMngr = TMserverMngr
omniORB.registerSkeleton(TMserverMngr._NP_RepositoryId, TMserverMngr)
del TMserverMngr
__name__ = "ITM_PRO"

#
# End of module "ITM_PRO"
#
__name__ = "ITM_PRO_idl"

_exported_modules = ( "ITM_PRO", )

# The end.
