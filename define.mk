ifeq ("$(PJ_ROOT)", "")
PJ_ROOT=`pwd`
endif

ifeq ("$(PJ_BUILDER)", "")
PJ_BUILDER=`whoami`
endif

ifeq ("$(PJ_SH_CP)", "")
PJ_SH_CP=cp -avrf
endif

ifeq ("$(PJ_SH_MKDIR)", "")
PJ_SH_MKDIR=mkdir -p
endif

ifeq ("$(PJ_SH_RMDIR)", "")
PJ_SH_RMDIR=rm -rf
endif

ifeq ("$(PJ_SH_RM)", "")
PJ_SH_RM=rm -f
endif

