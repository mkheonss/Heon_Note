"""
- Sync 대상
df_in_s : Select (FROM.[Item].[Plan Group] * FROM.[Item].[Item] * FROM.Location.[Location Type].[MF].relatedmembers(Location) * FROM.[Time].[Week] * FROM.[Activity1].[Activity1] * FROM.[Activity2].[Activity2].filter(#.Name startswith "RT_") * FROM.[Activity3].[Activity3] * FROM.[Documents].[OrderlineID] * TO.[Location].[Location] * TO.[Time].[Week] * TO.[Documents].[OrderlineID] * TO.[Activity1].[Activity1] * TO.[Activity2].[Activity2] * TO.[Activity3].[Activity3]) on row, ({Edge.[SOP Sync].[SOP Sync_SOP Qty] , Edge.[SOP Sync].[SOP Sync_Mfg OrderlineID] , Edge.[SOP Sync].[SOP Sync_SOP OrderlineID]}) on column where {RelationshipType.[SOP Sync], Version.[Version Name]};
- Capa Consume
df_in_cc : Select ( &MFLocation * [Time].[Week]* [Resource].[Resource].filter(#.Name startswith "MLC") * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Capacity Consumption Quantity Plan Output], Measure.[W Resource Consumed Quantity Per]}) on column where { [Version].[Version Name] };

df_out :

DELETE DATA FOR RELATIONSHIPTYPE [Capa Sync] WHERE { [Version].[Version Name].[CWV_MP] };

EXEC plugin instance [PY_MG_CapaSync]
for measures {[Capa Sync].[Capa Sync_SOP Qty]}
using scope ( [Version].[Version Name].[CWV_MP] * [Item].[Plan Group].filter(#.Name == "1") )
using arguments {(paramOutVersion, "CWV_MP"), (paramLocation, ""), (paramOthersLocation, ""), (paramSeq, "0"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};


EXEC plugin instance [PY_MG_CapaSync]
for measures {[Capa Sync].[Capa Sync_SOP Qty]}
using scope ( [Version].[Version Name].[CWV_MP] * [Item].[Plan Group].filter(#.Name == "1") )
using arguments {(paramOutVersion, "CWV_MP"), (paramLocation, "P551"), (paramOthersLocation, ""), (paramSeq, "0"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

EXEC plugin instance [PY_MG_CapaSync]
for measures {[Capa Sync].[Capa Sync_SOP Qty]}
using scope ( [Version].[Version Name].[CWV_MP] * [Item].[Plan Group].filter(#.Name == "1") )
using arguments {(paramOutVersion, "CWV_MP"), (paramLocation, "P306"), (paramOthersLocation, ""), (paramSeq, "1"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

EXEC plugin instance [PY_MG_CapaSync]
for measures {[Capa Sync].[Capa Sync_SOP Qty]}
using scope ( [Version].[Version Name].[CWV_MP] * [Item].[Plan Group].filter(#.Name == "1") )
using arguments {(paramOutVersion, "CWV_MP"), (paramLocation, ""), (paramOthersLocation, "P551,P306"), (paramSeq, "2"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

LPS Output

paramLocation : P551, P306


* V2
- 속도 개선을 위해서 at으로 변경
- 정렬 기준이 같을 경우 정렬 순서가 1이 없는 문제로 rank(method="first") 사용

* V3
- Capa Consume 에 없으면 전체를 제외하고 마지막에 넣도록 로직 개선
- Capa Consume 에서 "Resource.[Resource]" 에서 MLC_P54B@P54B 와 같이 MLC_??@?? 인 데이타는 제외하는 로직 개선

* V4 : 2025.5.15
- Capa Sync_Mfg OrderlineID2, Capa Sync_SOP OrderlineID2 추가
    - Capa Sync_Mfg OrderlineID : LPSM + SEQ(9자리)
    - Capa Sync_SOP OrderlineID : LPSS + SEQ(9자리)
    --> LPSM, LPSS가 아닌것들은 기존값으로

* V5 : 2025.5.16
- Item/Capa Cons 데이타 가져올때 SOP Sync Mfg Plan의 MAX 이후 날짜는 가져오지 않기
- from.[Week1].[Week1]는 넣지 않기 -- from.week와 동일하게 Update (Deug Mode 구분??) : from.[Week].[Week] 까지 Sum 을 하고 from.[Week1].[Week1] 에 같은 값을 넣는다.

* V7 : 2025.6.9
- for idx, row in df_in_s.iterrows(): 로 변경
- 결과를 list 에 넣어서 마지막에 DataFrame 로 변경

"""

import pandas as pd
import os
import traceback
import warnings
import numpy as np
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_CapaSync'

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()

logger.Start()

########################################################################################################################
# 공통 함수 정의
########################################################################################################################
# 스트링을 넘겨준다.
def gfn_get_str(val):
    if (type(val) is str):
        return val
    elif (type(val) is float):
        if (pd.isna(val)):
            return ""
        else:
            return str(val)

def gfn_lpad(val, width, fillchar='0'):
    return str(val).rjust(width, fillchar)
########################################################################################################################
# 함수 정의
########################################################################################################################

# "MLC_AAA@BBB" AAA 와 BBB 가 같은지 체크
def fn_equalFlag(data:str):
    result = "N"

    split1 = data.split("@")
    split2 = split1[0].split("_")

    if split2[1] == split1[1]:
        result = "Y"

    return result

try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))
    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if common.gfn_get_isLocal():
        df_in_s = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_s.csv", encoding="UTF-8")
        df_in_cc = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_cc.csv", encoding="UTF-8")

        # 케이스별 테스트
        # df_in_s = df_in_s.loc[(df_in_s["from.[Activity3].[Activity3]"] == "QN55QN90FAGXZS") & (df_in_s["from.[Activity1].[Activity1]"] == "QN55QN90FAGXZS_CA01")].copy()
        # df_in_cc = df_in_cc.loc[(df_in_cc["Activity3.[Activity3]"] == "QN55QN90FAGXZS") & (df_in_cc["Activity1.[Activity1]"] == "QN55QN90FAGXZS_CA01")].copy()

        paramOutVersion = "CWV_MP"
        paramLocation = ""
        paramOthersLocation = ""
        paramSeq = "0"

    # Location 파라미터로 필터
    if paramLocation != "":
        df_in_s = df_in_s[df_in_s["from.[Location].[Location]"].isin(paramLocation.split(","))].reset_index(drop=True)
        df_in_cc = df_in_cc[df_in_cc["Location.[Location]"].isin(paramLocation.split(","))].reset_index(drop=True)

    # Location 제외 파라미터로 필터
    if paramOthersLocation != "":
        df_in_s = df_in_s[~df_in_s["from.[Location].[Location]"].isin(paramOthersLocation.split(","))].reset_index(drop=True)
        df_in_cc = df_in_cc[~df_in_cc["Location.[Location]"].isin(paramOthersLocation.split(","))].reset_index(drop=True)

    vdCommon.gfn_saveDf(df_in_s, "df_in_s", True)
    vdCommon.gfn_saveDf(df_in_cc, "df_in_cc", True)

    # (V5) SOP Sync 에서 주차 Max 값을 구한다.
    df_in_s_max = df_in_s.groupby(["from.[Location].[Location]", "from.[Activity1].[Activity1]", "from.[Activity2].[Activity2]",
                                   "from.[Activity3].[Activity3]", "from.[Documents].[OrderlineID]"])["from.[Time].[Week]"].max().reset_index()
    vdCommon.gfn_saveDf(df_in_s_max, "SOP Sync_Week Max", True)

    # (V5) Capa Consume 은 SOP Sync 에서 구한 Max 값보다 작은 데이타만 가지고 온다.
    df_in_cc = df_in_cc.merge(df_in_s_max, how='inner',
                                 left_on=["Location.[Location]", "Activity1.[Activity1]", "Activity2.[Activity2]", "Activity3.[Activity3]", "Documents.[OrderlineID]"],
                                 right_on=["from.[Location].[Location]", "from.[Activity1].[Activity1]", "from.[Activity2].[Activity2]", "from.[Activity3].[Activity3]", "from.[Documents].[OrderlineID]"])
    df_in_cc = df_in_cc.loc[(df_in_cc["Time.[Week]"] <= df_in_cc["from.[Time].[Week]"])].copy().reset_index(drop=True)
    vdCommon.gfn_saveDf(df_in_cc, "Capa Consume_Under Max Week", True)

    # Capa Consume 에서 "Resource.[Resource]" 에서 MLC_P54B@P54B 와 같이 MLC_??@?? 인 데이타는 제외하는 로직 개선
    df_in_cc["Equal Flag"] = df_in_cc["Resource.[Resource]"].apply(lambda val: fn_equalFlag(val))
    df_in_cc = df_in_cc.loc[(df_in_cc["Equal Flag"] == "N")].copy().reset_index(drop=True)
    df_in_cc.drop(labels=["Equal Flag"], axis=1, inplace=True)
    vdCommon.gfn_saveDf(df_in_cc, "df_in_cc delete Equal Flag", True)

    # Sync 주자 역순으로 정렬해서 Rank 를 구한다.
    df_in_s = df_in_s.sort_values(by=["from.[Location].[Location]", "from.[Item].[Item]",
                                        "from.[Activity1].[Activity1]", "from.[Activity2].[Activity2]", "from.[Activity3].[Activity3]", "from.[Documents].[OrderlineID]", "from.[Time].[Week]"],
                                  ascending=[True, True, True, True, True, True, False]).reset_index(drop=True)
    df_in_s['from.[Time].[Week]'] = df_in_s['from.[Time].[Week]'].astype(int)
    df_in_s['Rank'] = df_in_s.groupby(["from.[Location].[Location]", "from.[Item].[Item]",
                                            "from.[Activity1].[Activity1]", "from.[Activity2].[Activity2]", "from.[Activity3].[Activity3]", "from.[Documents].[OrderlineID]"])["from.[Time].[Week]"].rank(method="first", ascending=False)
    df_in_s["Org SOP Sync.[SOP Sync_SOP Qty]"] = df_in_s["SOP Sync.[SOP Sync_SOP Qty]"]
    vdCommon.gfn_saveDf(df_in_s, "sync sort", True)

    # Capa Consume 주자 역순으로 정렬해서 Rank 를 구한다.
    df_in_cc = df_in_cc.sort_values(by=["Location.[Location]",
                                              "Activity1.[Activity1]", "Activity2.[Activity2]", "Activity3.[Activity3]", "Documents.[OrderlineID]", "Time.[Week]", "Resource.[Resource]"],
                                  ascending=[True, True, True, True, True, False, True]).reset_index(drop=True)
    df_in_cc['Time.[Week]'] = df_in_cc['Time.[Week]'].astype(int)
    df_in_cc['Rank'] = df_in_cc.groupby(["Location.[Location]",
                                                 "Activity1.[Activity1]", "Activity2.[Activity2]", "Activity3.[Activity3]", "Documents.[OrderlineID]"])["Time.[Week]"].rank(method="first", ascending=False)
    df_in_cc["Capa Qty"] = round(df_in_cc["W Capacity Consumption Quantity Plan Output"] / df_in_cc["W Resource Consumed Quantity Per"], 0)
    df_in_cc["Org Capa Qty"] = df_in_cc["Capa Qty"]
    vdCommon.gfn_saveDf(df_in_cc, "CapaConsume sort", True)

    # SOP Sync 를 Capa Consume 이 있는 것과 없는 것으로 분리
    # 키 중복 제거
    df_in_cc_dup = df_in_cc[["Location.[Location]", "Activity1.[Activity1]", "Activity2.[Activity2]", "Activity3.[Activity3]", "Documents.[OrderlineID]"]].copy()
    df_in_cc_dup = df_in_cc_dup.drop_duplicates()
    df_in_cc_dup["Key"] = "Y"
    vdCommon.gfn_saveDf(df_in_cc_dup, "df_in_cc_dup", True)

    df_in_s_merge = df_in_s.merge(df_in_cc_dup, how="left",
                                 left_on=["from.[Location].[Location]", "from.[Activity1].[Activity1]", "from.[Activity2].[Activity2]", "from.[Activity3].[Activity3]", "from.[Documents].[OrderlineID]"],
                                 right_on=["Location.[Location]", "Activity1.[Activity1]", "Activity2.[Activity2]", "Activity3.[Activity3]", "Documents.[OrderlineID]"])
    df_in_s_merge.drop(labels=["Location.[Location]", "Activity1.[Activity1]", "Activity2.[Activity2]", "Activity3.[Activity3]", "Documents.[OrderlineID]"], axis=1, inplace=True)
    vdCommon.gfn_saveDf(df_in_s_merge, "df_in_s_merge", True)

    df_in_s_merge["Key"].fillna(value="", inplace=True)
    df_in_s = df_in_s_merge.loc[(df_in_s_merge["Key"] == "Y")].copy().reset_index(drop=True)
    df_in_s.drop(labels=["Key"], axis=1, inplace=True)
    df_in_s_o = df_in_s_merge.loc[(df_in_s_merge["Key"] == "")].copy()
    df_in_s_o.drop(labels=["Key"], axis=1, inplace=True)

    vdCommon.gfn_saveDf(df_in_s, "sync Data", True)
    vdCommon.gfn_saveDf(df_in_s_o, "sync Data No Capa Consume", True)

    # df_out 생성
    df_out = pd.DataFrame([], columns=["Version.[Version Name]",
                                                "from.[Item].[Item]", "from.[Location].[Location]", "from.[Resource].[Resource]", "from.[Documents].[OrderlineID]",
                                                "from.[Activity1].[Activity1]", "from.[Activity2].[Activity2]", "from.[Activity3].[Activity3]", "from.[Time].[Week]", "from.[Week1].[Week1]",
                                                "to.[Location].[Location]", "to.[Documents].[OrderlineID]", "to.[Time].[Week]", "to.[Activity1].[Activity1]", "to.[Activity2].[Activity2]", "to.[Activity3].[Activity3]",
                                                "Capa Sync.[Capa Sync_Mfg OrderlineID]", "Capa Sync.[Capa Sync_SOP OrderlineID]", "Capa Sync.[Capa Sync_SOP Qty]",
                                                "Capa Sync.[Capa Sync_Capa Consume Qty]", "Capa Sync.[Capa Sync_Capa Consume Per]"])
    df_out_temp = pd.DataFrame([], columns=["Version.[Version Name]",
                                                    "from.[Item].[Item]", "from.[Location].[Location]", "from.[Resource].[Resource]", "from.[Documents].[OrderlineID]",
                                                    "from.[Activity1].[Activity1]", "from.[Activity2].[Activity2]", "from.[Activity3].[Activity3]", "from.[Time].[Week]", "from.[Week1].[Week1]",
                                                    "to.[Location].[Location]", "to.[Documents].[OrderlineID]", "to.[Time].[Week]", "to.[Activity1].[Activity1]", "to.[Activity2].[Activity2]", "to.[Activity3].[Activity3]",
                                                    "Capa Sync.[Capa Sync_Mfg OrderlineID]", "Capa Sync.[Capa Sync_SOP OrderlineID]", "Capa Sync.[Capa Sync_SOP Qty]",
                                                    "Capa Sync.[Capa Sync_Capa Consume Qty]", "Capa Sync.[Capa Sync_Capa Consume Per]"])

    # Capa Consume 를 기준으로 index 를 가지는 HashMap 구성
    hm_index = {}
    df_work_index = df_in_cc.loc[(df_in_cc["Rank"] == 1)].copy()
    for idx in df_work_index.index:
        key = (df_work_index.at[idx, "Location.[Location]"] + df_work_index.at[idx, "Documents.[OrderlineID]"] +
               df_work_index.at[idx, "Activity1.[Activity1]"] + df_work_index.at[idx, "Activity2.[Activity2]"] + df_work_index.at[idx, "Activity3.[Activity3]"])
        hm_index[key] = idx
    # print(hm_index)

    out_list = []

    f_idx = -1
    rate_count = round(df_in_s.shape[0] / 100, 0)
    while_cnt = 0
    # (V7) df_in_s.iterrows 로 로직 변경
    for idx, row in df_in_s.iterrows():
        # Capa Consume 의 시작위치를 찾는다.
        if row["Rank"] == 1:
            # HashMap 에서 index 를 가져옴
            key = (row["from.[Location].[Location]"] + row["from.[Documents].[OrderlineID]"] +
                   row["from.[Activity1].[Activity1]"] + row["from.[Activity2].[Activity2]"] + row["from.[Activity3].[Activity3]"])
            keyData = (hm_index.get(key))
            if keyData != None:
                f_idx = keyData
            else:
                f_idx = -1

        # 생산 Qty
        item = row["from.[Item].[Item]"]
        location = row["from.[Location].[Location]"]
        document = row["from.[Documents].[OrderlineID]"]
        activity1 = row["from.[Activity1].[Activity1]"]
        activity2 = row["from.[Activity2].[Activity2]"]
        activity3 = row["from.[Activity3].[Activity3]"]
        time = row["from.[Time].[Week]"]
        to_time = row["to.[Time].[Week]"]
        to_location = row["to.[Location].[Location]"]
        to_document = row["to.[Documents].[OrderlineID]"]
        to_activity1 = row["to.[Activity1].[Activity1]"]
        to_activity2 = row["to.[Activity2].[Activity2]"]
        to_activity3 = row["to.[Activity3].[Activity3]"]
        mfg_oi = row["SOP Sync.[SOP Sync_Mfg OrderlineID]"]
        sop_oi = row["SOP Sync.[SOP Sync_SOP OrderlineID]"]
        qty = row["SOP Sync.[SOP Sync_SOP Qty]"]

        # Capa 에서 생산 Qty 를 뺀다.
        if ( f_idx > -1 and f_idx < df_in_cc.shape[0] ):
            while ( row["from.[Location].[Location]"] == df_in_cc.at[f_idx, "Location.[Location]"]
                    and row["from.[Documents].[OrderlineID]"] == df_in_cc.at[f_idx, "Documents.[OrderlineID]"]
                    and row["from.[Activity1].[Activity1]"] == df_in_cc.at[f_idx, "Activity1.[Activity1]"]
                    and row["from.[Activity2].[Activity2]"] == df_in_cc.at[f_idx, "Activity2.[Activity2]"]
                    and row["from.[Activity3].[Activity3]"] == df_in_cc.at[f_idx, "Activity3.[Activity3]"] ):
                capa_qty = df_in_cc.at[f_idx, "Capa Qty"]
                resource = df_in_cc.at[f_idx, "Resource.[Resource]"]
                capa_time = df_in_cc.at[f_idx, "Time.[Week]"]
                capa_consume_per = df_in_cc.at[f_idx, "W Resource Consumed Quantity Per"]

                while_cnt = while_cnt + 1

                if qty == capa_qty:
                    out_list.append([paramOutVersion, item, location, resource, document, activity1, activity2, activity3, time, capa_time,
                                                         to_location, to_document, to_time, to_activity1, to_activity2, to_activity3,
                                                         mfg_oi, sop_oi, capa_qty,
                                                         capa_consume_per * capa_qty, capa_consume_per])
                    df_in_s.at[idx, "SOP Sync.[SOP Sync_SOP Qty]"] = 0
                    df_in_cc.at[f_idx, "Capa Qty"] = 0
                    f_idx = f_idx + 1

                    break
                elif qty > capa_qty:
                    out_list.append([paramOutVersion, item, location, resource, document, activity1, activity2, activity3, time, capa_time,
                                                         to_location, to_document, to_time, to_activity1, to_activity2, to_activity3,
                                                         mfg_oi, sop_oi, capa_qty,
                                                         capa_consume_per * capa_qty, capa_consume_per])
                    df_in_s.at[idx, "SOP Sync.[SOP Sync_SOP Qty]"] = qty - capa_qty
                    df_in_cc.at[f_idx, "Capa Qty"] = 0

                    qty = qty - capa_qty
                    f_idx = f_idx + 1
                else:
                    out_list.append([paramOutVersion, item, location, resource, document, activity1, activity2, activity3, time, capa_time,
                                                         to_location, to_document, to_time, to_activity1, to_activity2, to_activity3,
                                                         mfg_oi, sop_oi, qty,
                                                         capa_consume_per * qty, capa_consume_per])
                    df_in_s.at[idx, "SOP Sync.[SOP Sync_SOP Qty]"] = 0
                    df_in_cc.at[f_idx, "Capa Qty"] = capa_qty - qty

                    break

                if f_idx >= df_in_cc.shape[0]:
                    break

        if rate_count >  0:
            if idx % rate_count == 0:
                vdCommon.gfn_stepLog("Process Rate : " + str(round(idx * 100 / df_in_s.shape[0])) + "%" + " , idx : " + str(idx) + " , while_cnt : " + str(while_cnt))
                while_cnt = 0

    # (V7) 결과를 리스트 데이타를 기준으로 생성
    df_out = pd.DataFrame(out_list, columns=["Version.[Version Name]",
                                                "from.[Item].[Item]", "from.[Location].[Location]", "from.[Resource].[Resource]", "from.[Documents].[OrderlineID]",
                                                "from.[Activity1].[Activity1]", "from.[Activity2].[Activity2]", "from.[Activity3].[Activity3]", "from.[Time].[Week]", "from.[Week1].[Week1]",
                                                "to.[Location].[Location]", "to.[Documents].[OrderlineID]", "to.[Time].[Week]", "to.[Activity1].[Activity1]", "to.[Activity2].[Activity2]", "to.[Activity3].[Activity3]",
                                                "Capa Sync.[Capa Sync_Mfg OrderlineID]", "Capa Sync.[Capa Sync_SOP OrderlineID]", "Capa Sync.[Capa Sync_SOP Qty]",
                                                "Capa Sync.[Capa Sync_Capa Consume Qty]", "Capa Sync.[Capa Sync_Capa Consume Per]"])

    vdCommon.gfn_saveDf(df_in_s, "sync result", True)
    vdCommon.gfn_saveDf(df_in_cc, "CapaConsume result", True)
    vdCommon.gfn_saveDf(df_out, "df_out calc", True)

    # (V5) from.[Week1].[Week1]를 제외하고 Sum 을 구하도록
    df_out = (df_out.groupby(["Version.[Version Name]",
                                "from.[Item].[Item]", "from.[Location].[Location]", "from.[Resource].[Resource]", "from.[Documents].[OrderlineID]",
                                "from.[Activity1].[Activity1]", "from.[Activity2].[Activity2]", "from.[Activity3].[Activity3]", "from.[Time].[Week]",
                                "to.[Location].[Location]", "to.[Documents].[OrderlineID]", "to.[Time].[Week]", "to.[Activity1].[Activity1]", "to.[Activity2].[Activity2]", "to.[Activity3].[Activity3]",
                                "Capa Sync.[Capa Sync_Mfg OrderlineID]", "Capa Sync.[Capa Sync_SOP OrderlineID]"]).
                            agg({"Capa Sync.[Capa Sync_SOP Qty]" : "sum", "Capa Sync.[Capa Sync_Capa Consume Qty]" : "sum", "Capa Sync.[Capa Sync_Capa Consume Per]" : "max"}).reset_index())
    df_out.insert(0, "from.[Week1].[Week1]", "")
    df_out["from.[Week1].[Week1]"] = df_out["from.[Time].[Week]"]
    vdCommon.gfn_saveDf(df_out, "df_out sum", True)

    # 계산로직 전에 제외할 데이타를 추가해줌
    df_in_s = pd.concat([df_in_s, df_in_s_o])

    # SOP Sync 에서 남은 수량을 넣어준다.
    df_in_s_work = df_in_s.loc[(df_in_s["SOP Sync.[SOP Sync_SOP Qty]"] > 0)].copy()
    # vdCommon.gfn_saveDf(df_in_s_work, "sync remain", True)
    df_in_s_work["Version.[Version Name]"] = paramOutVersion
    df_in_s_work["from.[Resource].[Resource]"] = "-"
    df_in_s_work["Capa Sync.[Capa Sync_Capa Consume Qty]"] = 0
    df_in_s_work["Capa Sync.[Capa Sync_Capa Consume Per]"] = 0
    df_in_s_work["from.[Week1].[Week1]"] = df_in_s_work["from.[Time].[Week]"]
    df_in_s_work.rename(columns={"SOP Sync.[SOP Sync_SOP Qty]" : "Capa Sync.[Capa Sync_SOP Qty]",
                                    "SOP Sync.[SOP Sync_Mfg OrderlineID]" : "Capa Sync.[Capa Sync_Mfg OrderlineID]",
                                    "SOP Sync.[SOP Sync_SOP OrderlineID]" : "Capa Sync.[Capa Sync_SOP OrderlineID]"}, inplace=True)
    df_in_s_work.drop(columns=["Rank","Org SOP Sync.[SOP Sync_SOP Qty]", "Item.[Plan Group]"], axis=1, inplace=True)
    vdCommon.gfn_saveDf(df_in_s_work, "sync remain", True)

    # 결과를 합친다.
    df_out = pd.concat([df_out, df_in_s_work])

    # 결과 정렬
    df_out = df_out.sort_values(by=["from.[Location].[Location]", "from.[Activity1].[Activity1]", "from.[Activity2].[Activity2]", "from.[Activity3].[Activity3]", "from.[Documents].[OrderlineID]", "from.[Time].[Week]", "from.[Resource].[Resource]"],
                                  ascending=[True, True, True, True, True, False, False]).reset_index(drop=True)

    # (V4) Mfg OrderlineID2, SOP OrderlineID2 에 새로운 정렬 기준 세팅 : 000000001 포맷의 데이타를 새로 만듬
    if int(paramSeq) == 0:
        startSeq = 1
    else:
        startSeq = (int(paramSeq) + 1) * 100000 + 1

    df_out["Seq"] = [gfn_lpad(str(i), 9, "0") for i in range(startSeq, len(df_out) + startSeq)]

    df_out["Capa Sync.[Capa Sync_Mfg OrderlineID2]"] = np.where(df_out["Capa Sync.[Capa Sync_Mfg OrderlineID]"].str.startswith("LPSM_"), "LPSM_" + df_out["Seq"], df_out["Capa Sync.[Capa Sync_Mfg OrderlineID]"])
    df_out["Capa Sync.[Capa Sync_SOP OrderlineID2]"] = np.where(df_out["Capa Sync.[Capa Sync_SOP OrderlineID]"].str.startswith("LPSS_"), "LPSS_" + df_out["Seq"], df_out["Capa Sync.[Capa Sync_SOP OrderlineID]"])
    df_out.drop(columns=["Seq"], axis=1, inplace=True)

    # 총량 데이타 비교
    df_c_t1_d1 = df_in_s.groupby(["from.[Location].[Location]", "from.[Activity1].[Activity1]", "from.[Activity2].[Activity2]", "from.[Activity3].[Activity3]"], as_index=False)[["Org SOP Sync.[SOP Sync_SOP Qty]"]].sum()
    df_c_t1_d2 = df_in_cc.groupby(["Location.[Location]", "Activity1.[Activity1]", "Activity2.[Activity2]", "Activity3.[Activity3]"], as_index=False)[["Org Capa Qty"]].sum()
    df_c_t1_d3 = df_out.groupby(["from.[Location].[Location]", "from.[Activity1].[Activity1]", "from.[Activity2].[Activity2]", "from.[Activity3].[Activity3]"], as_index=False)[["Capa Sync.[Capa Sync_SOP Qty]"]].sum()
    df_c_t1 = df_c_t1_d1.merge(df_c_t1_d2, how='left',
                              left_on=["from.[Location].[Location]", "from.[Activity1].[Activity1]", "from.[Activity2].[Activity2]", "from.[Activity3].[Activity3]"],
                              right_on=["Location.[Location]", "Activity1.[Activity1]", "Activity2.[Activity2]", "Activity3.[Activity3]"])
    df_c_t1 = df_c_t1.merge(df_c_t1_d3, how='left',
                              left_on=["from.[Location].[Location]", "from.[Activity1].[Activity1]", "from.[Activity2].[Activity2]", "from.[Activity3].[Activity3]"],
                              right_on=["from.[Location].[Location]", "from.[Activity1].[Activity1]", "from.[Activity2].[Activity2]", "from.[Activity3].[Activity3]"])
    df_c_t1 = df_c_t1.loc[(df_c_t1["Org SOP Sync.[SOP Sync_SOP Qty]"] != df_c_t1["Capa Sync.[Capa Sync_SOP Qty]"])].copy()
    if df_c_t1.shape[0] > 0 :
        vdCommon.gfn_saveDf(df_c_t1, "Compare - Error", True)

    vdCommon.gfn_saveDf(df_out, "df_out", True)

    vdCommon.gfn_stepLog('plugin Execution End')
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.info())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out = pd.DataFrame([], columns=[])
finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()

    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()

    logger.Finish()
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')




