/* Biz: gscm.r.pi.cot.cotb.db.DCOT020.S002 COM상세(월 조회) */
/* IO: Kim Junsu,2020-08-06T14:43:46(Kim Junsu,2020-08-06T14:43:46) */
WITH WITH_ACT_1 AS
(
       SELECT COST_PLN_YY
            , VER_CD
            , PLN_REV
            , COST_PLN_YM
            , COST_WEEK_GBN_CD
            , PLN_ACTOUT_GBN_CD
            , TGT_YM
            , FAMILY_CD
            , FAB_ID
            , PKG_DEN_CD
            , FAB_DEN_CD
            , CELL_LAYER_TYP_CD
            , PROD_MODE_CD
            , TECH_CD
            , GEN_CD
            , NET_DIE_300_CNT
            , PKG_TYP_CD2
            , MOD_TYP_CD
            , MOD_STRUCT_TYP_CD
            , BIZ_TYP_CD
            , COST_AREA_CD
            , COST_ACCT_CD
            , COST_QTY
            , COST_EQ_QTY
            , USD_COST_AMT
            , LOOSE_YN
            , CRT_TM
            , CRT_USER_ID
            , CHG_TM
            , CHG_USER_ID
            , COST_AMT
         FROM RPO_ERP_COMFG_PROD
        WHERE 1                 = 1
          AND LOOSE_YN          = 'Y'
          AND TGT_YM           >= '202401'
          AND TGT_YM            < '202403'
          AND PLN_ACTOUT_GBN_CD = 'ACTOUT'
          AND COST_AREA_CD     <> '*'
          AND COST_ACCT_CD     <> '*'
)
, WITH_ACT_B1 AS
(
       SELECT COST_PLN_YY
            , VER_CD
            , PLN_REV
            , COST_PLN_YM
            , COST_WEEK_GBN_CD
            , PLN_ACTOUT_GBN_CD
            , TGT_YM
            , FAMILY_CD
            , FAB_ID
            , PKG_DEN_CD
            , FAB_DEN_CD
            , CELL_LAYER_TYP_CD
            , PROD_MODE_CD
            , TECH_CD
            , GEN_CD
            , NET_DIE_300_CNT
            , PKG_TYP_CD2
            , MOD_TYP_CD
            , MOD_STRUCT_TYP_CD
            , BIZ_TYP_CD
            , COST_AREA_CD
            , COST_ACCT_CD
            , COST_QTY
            , COST_EQ_QTY
            , USD_COST_AMT
            , LOOSE_YN
            , CRT_TM
            , CRT_USER_ID
            , CHG_TM
            , CHG_USER_ID
            , COST_AMT
         FROM RPO_ERP_COMFG_PROD
        WHERE 1                 = 1
          AND LOOSE_YN          = 'Y'
          AND TGT_YM           >= '202401'
          AND TGT_YM            < '202403'
          AND PLN_ACTOUT_GBN_CD = 'ACTOUT'
          AND COST_AREA_CD      = '*'
          AND COST_ACCT_CD      = '*'
)
, WITH_PLN_1 AS
(
       SELECT COST_PLN_YY
            , VER_CD
            , PLN_REV
            , COST_PLN_YM
            , COST_WEEK_GBN_CD
            , PLN_ACTOUT_GBN_CD
            , TGT_YM
            , FAMILY_CD
            , FAB_ID
            , PKG_DEN_CD
            , FAB_DEN_CD
            , CELL_LAYER_TYP_CD
            , PROD_MODE_CD
            , TECH_CD
            , GEN_CD
            , NET_DIE_300_CNT
            , PKG_TYP_CD2
            , MOD_TYP_CD
            , MOD_STRUCT_TYP_CD
            , BIZ_TYP_CD
            , COST_AREA_CD
            , COST_ACCT_CD
            , COST_QTY
            , COST_EQ_QTY
            , USD_COST_AMT
            , LOOSE_YN
            , CRT_TM
            , CRT_USER_ID
            , CHG_TM
            , CHG_USER_ID
            , COST_AMT
         FROM RPO_ERP_COMFG_PROD
        WHERE 1                 = 1
          AND LOOSE_YN          = 'Y'
          AND TGT_YM           >= '202403'
          AND TGT_YM           <= '202412'
          AND PLN_REV           = 'RP-202403-W2-SNC-30'
          AND COST_PLN_YY       = '2024'
          AND VER_CD            = 'D31'
          AND PLN_ACTOUT_GBN_CD = 'PLN'
          AND COST_AREA_CD     <> '*'
          AND COST_ACCT_CD     <> '*'
)
, WITH_PLN_2 AS
(
       SELECT COST_PLN_YY
            , VER_CD
            , PLN_REV
            , COST_PLN_YM
            , COST_WEEK_GBN_CD
            , PLN_ACTOUT_GBN_CD
            , TGT_YM
            , FAMILY_CD
            , FAB_ID
            , PKG_DEN_CD
            , FAB_DEN_CD
            , CELL_LAYER_TYP_CD
            , PROD_MODE_CD
            , TECH_CD
            , GEN_CD
            , NET_DIE_300_CNT
            , PKG_TYP_CD2
            , MOD_TYP_CD
            , MOD_STRUCT_TYP_CD
            , BIZ_TYP_CD
            , COST_AREA_CD
            , COST_ACCT_CD
            , COST_QTY
            , COST_EQ_QTY
            , USD_COST_AMT
            , LOOSE_YN
            , CRT_TM
            , CRT_USER_ID
            , CHG_TM
            , CHG_USER_ID
            , COST_AMT
         FROM RPO_ERP_COMFG_PROD
        WHERE 1                 = 1
          AND LOOSE_YN          = 'Y'
          AND TGT_YM           >= '202403'
          AND TGT_YM           <= '202412'
          AND PLN_REV           = 'RP-202402-W2-SNC-37'
          AND COST_PLN_YY       = '2024'
          AND VER_CD            = 'D21'
          AND PLN_ACTOUT_GBN_CD = 'PLN'
          AND COST_AREA_CD     <> '*'
          AND COST_ACCT_CD     <> '*'
)
, WITH_PLN_B1 AS
(
       SELECT COST_PLN_YY
            , VER_CD
            , PLN_REV
            , COST_PLN_YM
            , COST_WEEK_GBN_CD
            , PLN_ACTOUT_GBN_CD
            , TGT_YM
            , FAMILY_CD
            , FAB_ID
            , PKG_DEN_CD
            , FAB_DEN_CD
            , CELL_LAYER_TYP_CD
            , PROD_MODE_CD
            , TECH_CD
            , GEN_CD
            , NET_DIE_300_CNT
            , PKG_TYP_CD2
            , MOD_TYP_CD
            , MOD_STRUCT_TYP_CD
            , BIZ_TYP_CD
            , COST_AREA_CD
            , COST_ACCT_CD
            , COST_QTY
            , COST_EQ_QTY
            , USD_COST_AMT
            , LOOSE_YN
            , CRT_TM
            , CRT_USER_ID
            , CHG_TM
            , CHG_USER_ID
            , COST_AMT
         FROM RPO_ERP_COMFG_PROD
        WHERE 1                 = 1
          AND LOOSE_YN          = 'Y'
          AND TGT_YM           >= '202403'
          AND TGT_YM           <= '202412'
          AND PLN_REV           = 'RP-202403-W2-SNC-30'
          AND COST_PLN_YY       = '2024'
          AND VER_CD            = 'D31'
          AND PLN_ACTOUT_GBN_CD = 'PLN'
          AND COST_AREA_CD      = '*'
          AND COST_ACCT_CD      = '*'
)
, WITH_PLN_B2 AS
(
       SELECT COST_PLN_YY
            , VER_CD
            , PLN_REV
            , COST_PLN_YM
            , COST_WEEK_GBN_CD
            , PLN_ACTOUT_GBN_CD
            , TGT_YM
            , FAMILY_CD
            , FAB_ID
            , PKG_DEN_CD
            , FAB_DEN_CD
            , CELL_LAYER_TYP_CD
            , PROD_MODE_CD
            , TECH_CD
            , GEN_CD
            , NET_DIE_300_CNT
            , PKG_TYP_CD2
            , MOD_TYP_CD
            , MOD_STRUCT_TYP_CD
            , BIZ_TYP_CD
            , COST_AREA_CD
            , COST_ACCT_CD
            , COST_QTY
            , COST_EQ_QTY
            , USD_COST_AMT
            , LOOSE_YN
            , CRT_TM
            , CRT_USER_ID
            , CHG_TM
            , CHG_USER_ID
            , COST_AMT
         FROM RPO_ERP_COMFG_PROD
        WHERE 1                 = 1
          AND LOOSE_YN          = 'Y'
          AND TGT_YM           >= '202403'
          AND TGT_YM           <= '202412'
          AND PLN_REV           = 'RP-202402-W2-SNC-37'
          AND COST_PLN_YY       = '2024'
          AND VER_CD            = 'D21'
          AND PLN_ACTOUT_GBN_CD = 'PLN'
          AND COST_AREA_CD      = '*'
          AND COST_ACCT_CD      = '*'
)
  SELECT A.*
    FROM(
                    SELECT FAMILY_CD
                         , FAB_ID
                         , TECH_CD
                         , FAB_DEN_CD
                         , CELL_LAYER_TYP_CD
                         , MEASURE
                         ,(
                           CASE
                                    WHEN REV1 = 'C'
                                    THEN((
                                             CASE
                                                      WHEN LAG(NVL(M202401, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) = 0
                                                      THEN 0
                                                      ELSE(LAG(NVL(M202401, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) /LAG(NVL(M202401, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 7), REV1))
                                             END) *100 - 100)
                                    ELSE NVL(M202401, 0)
                           END) AS M202401
                         ,(
                           CASE
                                    WHEN REV1 = 'C'
                                    THEN((
                                             CASE
                                                      WHEN LAG(NVL(M202402, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) = 0
                                                      THEN 0
                                                      ELSE(LAG(NVL(M202402, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) /LAG(NVL(M202402, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 7), REV1))
                                             END) *100 - 100)
                                    ELSE NVL(M202402, 0)
                           END) AS M202402
                         ,(
                           CASE
                                    WHEN REV1 = 'C'
                                    THEN((
                                             CASE
                                                      WHEN LAG(NVL(M202403, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) = 0
                                                      THEN 0
                                                      ELSE(LAG(NVL(M202403, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) /LAG(NVL(M202403, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 7), REV1))
                                             END) *100 - 100)
                                    ELSE NVL(M202403, 0)
                           END) AS M202403
                         ,(
                           CASE
                                    WHEN REV1 = 'C'
                                    THEN((
                                             CASE
                                                      WHEN LAG(NVL(M202404, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) = 0
                                                      THEN 0
                                                      ELSE(LAG(NVL(M202404, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) /LAG(NVL(M202404, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 7), REV1))
                                             END) *100 - 100)
                                    ELSE NVL(M202404, 0)
                           END) AS M202404
                         ,(
                           CASE
                                    WHEN REV1 = 'C'
                                    THEN((
                                             CASE
                                                      WHEN LAG(NVL(M202405, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) = 0
                                                      THEN 0
                                                      ELSE(LAG(NVL(M202405, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) /LAG(NVL(M202405, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 7), REV1))
                                             END) *100 - 100)
                                    ELSE NVL(M202405, 0)
                           END) AS M202405
                         ,(
                           CASE
                                    WHEN REV1 = 'C'
                                    THEN((
                                             CASE
                                                      WHEN LAG(NVL(M202406, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) = 0
                                                      THEN 0
                                                      ELSE(LAG(NVL(M202406, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) /LAG(NVL(M202406, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 7), REV1))
                                             END) *100 - 100)
                                    ELSE NVL(M202406, 0)
                           END) AS M202406
                         ,(
                           CASE
                                    WHEN REV1 = 'C'
                                    THEN((
                                             CASE
                                                      WHEN LAG(NVL(M202407, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) = 0
                                                      THEN 0
                                                      ELSE(LAG(NVL(M202407, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) /LAG(NVL(M202407, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 7), REV1))
                                             END) *100 - 100)
                                    ELSE NVL(M202407, 0)
                           END) AS M202407
                         ,(
                           CASE
                                    WHEN REV1 = 'C'
                                    THEN((
                                             CASE
                                                      WHEN LAG(NVL(M202408, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) = 0
                                                      THEN 0
                                                      ELSE(LAG(NVL(M202408, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) /LAG(NVL(M202408, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 7), REV1))
                                             END) *100 - 100)
                                    ELSE NVL(M202408, 0)
                           END) AS M202408
                         ,(
                           CASE
                                    WHEN REV1 = 'C'
                                    THEN((
                                             CASE
                                                      WHEN LAG(NVL(M202409, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) = 0
                                                      THEN 0
                                                      ELSE(LAG(NVL(M202409, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) /LAG(NVL(M202409, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 7), REV1))
                                             END) *100 - 100)
                                    ELSE NVL(M202409, 0)
                           END) AS M202409
                         ,(
                           CASE
                                    WHEN REV1 = 'C'
                                    THEN((
                                             CASE
                                                      WHEN LAG(NVL(M202410, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) = 0
                                                      THEN 0
                                                      ELSE(LAG(NVL(M202410, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) /LAG(NVL(M202410, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 7), REV1))
                                             END) *100 - 100)
                                    ELSE NVL(M202410, 0)
                           END) AS M202410
                         ,(
                           CASE
                                    WHEN REV1 = 'C'
                                    THEN((
                                             CASE
                                                      WHEN LAG(NVL(M202411, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) = 0
                                                      THEN 0
                                                      ELSE(LAG(NVL(M202411, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) /LAG(NVL(M202411, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 7), REV1))
                                             END) *100 - 100)
                                    ELSE NVL(M202411, 0)
                           END) AS M202411
                         ,(
                           CASE
                                    WHEN REV1 = 'C'
                                    THEN((
                                             CASE
                                                      WHEN LAG(NVL(M202412, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) = 0
                                                      THEN 0
                                                      ELSE(LAG(NVL(M202412, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                    , 1
                                                                                                                                                                    , 'FAB'
                                                                                                                                                                    , 2
                                                                                                                                                                    , 'WT'
                                                                                                                                                                    , 3
                                                                                                                                                                    , 'PKG'
                                                                                                                                                                    , 4
                                                                                                                                                                    , 'PKT'
                                                                                                                                                                    , 5
                                                                                                                                                                    , 'MOD'
                                                                                                                                                                    , 6
                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                    , 7), REV1) /LAG(NVL(M202412, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 7), REV1))
                                             END) *100 - 100)
                                    ELSE NVL(M202412, 0)
                           END) AS M202412
                         ,(
                           CASE
                                    WHEN REV1 = 'C'
                                    THEN((
                                             CASE
                                                      WHEN LAG(NVL(합계, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                               , 1
                                                                                                                                                               , 'PKG'
                                                                                                                                                               , 2
                                                                                                                                                               , 'P&T'
                                                                                                                                                               , 3
                                                                                                                                                               , 'MOD'
                                                                                                                                                               , 4
                                                                                                                                                               , 'FAB'
                                                                                                                                                               , 5
                                                                                                                                                               , 'WT'
                                                                                                                                                               , 6
                                                                                                                                                               , 'ASSY'
                                                                                                                                                               , 7
                                                                                                                                                               , 'RDL'
                                                                                                                                                               , 8
                                                                                                                                                               , 'TSV'
                                                                                                                                                               , 9
                                                                                                                                                               , 'PKT'
                                                                                                                                                               , 10
                                                                                                                                                               , '생산량(M)'
                                                                                                                                                               , 11), REV1) = 0
                                                      THEN 0
                                                      ELSE(LAG(NVL(합계, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                               , 1
                                                                                                                                                               , 'PKG'
                                                                                                                                                               , 2
                                                                                                                                                               , 'P&T'
                                                                                                                                                               , 3
                                                                                                                                                               , 'MOD'
                                                                                                                                                               , 4
                                                                                                                                                               , 'FAB'
                                                                                                                                                               , 5
                                                                                                                                                               , 'WT'
                                                                                                                                                               , 6
                                                                                                                                                               , 'ASSY'
                                                                                                                                                               , 7
                                                                                                                                                               , 'RDL'
                                                                                                                                                               , 8
                                                                                                                                                               , 'TSV'
                                                                                                                                                               , 9
                                                                                                                                                               , 'PKT'
                                                                                                                                                               , 10
                                                                                                                                                               , '생산량(M)'
                                                                                                                                                               , 11), REV1) / LAG(NVL(합계, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                             END) * 100 - 100)
                                    ELSE NVL(합계, 0)
                           END) AS 합계
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(변동비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                  , 1
                                                                                                                                                                                  , 'PKG'
                                                                                                                                                                                  , 2
                                                                                                                                                                                  , 'P&T'
                                                                                                                                                                                  , 3
                                                                                                                                                                                  , 'MOD'
                                                                                                                                                                                  , 4
                                                                                                                                                                                  , 'FAB'
                                                                                                                                                                                  , 5
                                                                                                                                                                                  , 'WT'
                                                                                                                                                                                  , 6
                                                                                                                                                                                  , 'ASSY'
                                                                                                                                                                                  , 7
                                                                                                                                                                                  , 'RDL'
                                                                                                                                                                                  , 8
                                                                                                                                                                                  , 'TSV'
                                                                                                                                                                                  , 9
                                                                                                                                                                                  , 'PKT'
                                                                                                                                                                                  , 10
                                                                                                                                                                                  , '생산량(M)'
                                                                                                                                                                                  , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(변동비, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                  , 1
                                                                                                                                                                                  , 'PKG'
                                                                                                                                                                                  , 2
                                                                                                                                                                                  , 'P&T'
                                                                                                                                                                                  , 3
                                                                                                                                                                                  , 'MOD'
                                                                                                                                                                                  , 4
                                                                                                                                                                                  , 'FAB'
                                                                                                                                                                                  , 5
                                                                                                                                                                                  , 'WT'
                                                                                                                                                                                  , 6
                                                                                                                                                                                  , 'ASSY'
                                                                                                                                                                                  , 7
                                                                                                                                                                                  , 'RDL'
                                                                                                                                                                                  , 8
                                                                                                                                                                                  , 'TSV'
                                                                                                                                                                                  , 9
                                                                                                                                                                                  , 'PKT'
                                                                                                                                                                                  , 10
                                                                                                                                                                                  , '생산량(M)'
                                                                                                                                                                                  , 11), REV1) / LAG(NVL(변동비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(변동비, 0)
                                             END)
                           END) AS 변동비
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(고정비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                  , 1
                                                                                                                                                                                  , 'PKG'
                                                                                                                                                                                  , 2
                                                                                                                                                                                  , 'P&T'
                                                                                                                                                                                  , 3
                                                                                                                                                                                  , 'MOD'
                                                                                                                                                                                  , 4
                                                                                                                                                                                  , 'FAB'
                                                                                                                                                                                  , 5
                                                                                                                                                                                  , 'WT'
                                                                                                                                                                                  , 6
                                                                                                                                                                                  , 'ASSY'
                                                                                                                                                                                  , 7
                                                                                                                                                                                  , 'RDL'
                                                                                                                                                                                  , 8
                                                                                                                                                                                  , 'TSV'
                                                                                                                                                                                  , 9
                                                                                                                                                                                  , 'PKT'
                                                                                                                                                                                  , 10
                                                                                                                                                                                  , '생산량(M)'
                                                                                                                                                                                  , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(고정비, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                  , 1
                                                                                                                                                                                  , 'PKG'
                                                                                                                                                                                  , 2
                                                                                                                                                                                  , 'P&T'
                                                                                                                                                                                  , 3
                                                                                                                                                                                  , 'MOD'
                                                                                                                                                                                  , 4
                                                                                                                                                                                  , 'FAB'
                                                                                                                                                                                  , 5
                                                                                                                                                                                  , 'WT'
                                                                                                                                                                                  , 6
                                                                                                                                                                                  , 'ASSY'
                                                                                                                                                                                  , 7
                                                                                                                                                                                  , 'RDL'
                                                                                                                                                                                  , 8
                                                                                                                                                                                  , 'TSV'
                                                                                                                                                                                  , 9
                                                                                                                                                                                  , 'PKT'
                                                                                                                                                                                  , 10
                                                                                                                                                                                  , '생산량(M)'
                                                                                                                                                                                  , 11), REV1) / LAG(NVL(고정비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(고정비, 0)
                                             END)
                           END) AS 고정비
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(TOTAL1, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                     , 1
                                                                                                                                                                                     , 'PKG'
                                                                                                                                                                                     , 2
                                                                                                                                                                                     , 'P&T'
                                                                                                                                                                                     , 3
                                                                                                                                                                                     , 'MOD'
                                                                                                                                                                                     , 4
                                                                                                                                                                                     , 'FAB'
                                                                                                                                                                                     , 5
                                                                                                                                                                                     , 'WT'
                                                                                                                                                                                     , 6
                                                                                                                                                                                     , 'ASSY'
                                                                                                                                                                                     , 7
                                                                                                                                                                                     , 'RDL'
                                                                                                                                                                                     , 8
                                                                                                                                                                                     , 'TSV'
                                                                                                                                                                                     , 9
                                                                                                                                                                                     , 'PKT'
                                                                                                                                                                                     , 10
                                                                                                                                                                                     , '생산량(M)'
                                                                                                                                                                                     , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(TOTAL1, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                     , 1
                                                                                                                                                                                     , 'PKG'
                                                                                                                                                                                     , 2
                                                                                                                                                                                     , 'P&T'
                                                                                                                                                                                     , 3
                                                                                                                                                                                     , 'MOD'
                                                                                                                                                                                     , 4
                                                                                                                                                                                     , 'FAB'
                                                                                                                                                                                     , 5
                                                                                                                                                                                     , 'WT'
                                                                                                                                                                                     , 6
                                                                                                                                                                                     , 'ASSY'
                                                                                                                                                                                     , 7
                                                                                                                                                                                     , 'RDL'
                                                                                                                                                                                     , 8
                                                                                                                                                                                     , 'TSV'
                                                                                                                                                                                     , 9
                                                                                                                                                                                     , 'PKT'
                                                                                                                                                                                     , 10
                                                                                                                                                                                     , '생산량(M)'
                                                                                                                                                                                     , 11), REV1) / LAG(NVL(TOTAL1, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(TOTAL1, 0)
                                             END)
                           END) AS TOTAL1
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(WAFER, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                    , 1
                                                                                                                                                                                    , 'PKG'
                                                                                                                                                                                    , 2
                                                                                                                                                                                    , 'P&T'
                                                                                                                                                                                    , 3
                                                                                                                                                                                    , 'MOD'
                                                                                                                                                                                    , 4
                                                                                                                                                                                    , 'FAB'
                                                                                                                                                                                    , 5
                                                                                                                                                                                    , 'WT'
                                                                                                                                                                                    , 6
                                                                                                                                                                                    , 'ASSY'
                                                                                                                                                                                    , 7
                                                                                                                                                                                    , 'RDL'
                                                                                                                                                                                    , 8
                                                                                                                                                                                    , 'TSV'
                                                                                                                                                                                    , 9
                                                                                                                                                                                    , 'PKT'
                                                                                                                                                                                    , 10
                                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                                    , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(WAFER, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                    , 1
                                                                                                                                                                                    , 'PKG'
                                                                                                                                                                                    , 2
                                                                                                                                                                                    , 'P&T'
                                                                                                                                                                                    , 3
                                                                                                                                                                                    , 'MOD'
                                                                                                                                                                                    , 4
                                                                                                                                                                                    , 'FAB'
                                                                                                                                                                                    , 5
                                                                                                                                                                                    , 'WT'
                                                                                                                                                                                    , 6
                                                                                                                                                                                    , 'ASSY'
                                                                                                                                                                                    , 7
                                                                                                                                                                                    , 'RDL'
                                                                                                                                                                                    , 8
                                                                                                                                                                                    , 'TSV'
                                                                                                                                                                                    , 9
                                                                                                                                                                                    , 'PKT'
                                                                                                                                                                                    , 10
                                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                                    , 11), REV1) / LAG(NVL(WAFER, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(WAFER, 0)
                                             END)
                           END) AS WAFER
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(기타재료비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                    , 1
                                                                                                                                                                                    , 'PKG'
                                                                                                                                                                                    , 2
                                                                                                                                                                                    , 'P&T'
                                                                                                                                                                                    , 3
                                                                                                                                                                                    , 'MOD'
                                                                                                                                                                                    , 4
                                                                                                                                                                                    , 'FAB'
                                                                                                                                                                                    , 5
                                                                                                                                                                                    , 'WT'
                                                                                                                                                                                    , 6
                                                                                                                                                                                    , 'ASSY'
                                                                                                                                                                                    , 7
                                                                                                                                                                                    , 'RDL'
                                                                                                                                                                                    , 8
                                                                                                                                                                                    , 'TSV'
                                                                                                                                                                                    , 9
                                                                                                                                                                                    , 'PKT'
                                                                                                                                                                                    , 10
                                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                                    , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(기타재료비, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                    , 1
                                                                                                                                                                                    , 'PKG'
                                                                                                                                                                                    , 2
                                                                                                                                                                                    , 'P&T'
                                                                                                                                                                                    , 3
                                                                                                                                                                                    , 'MOD'
                                                                                                                                                                                    , 4
                                                                                                                                                                                    , 'FAB'
                                                                                                                                                                                    , 5
                                                                                                                                                                                    , 'WT'
                                                                                                                                                                                    , 6
                                                                                                                                                                                    , 'ASSY'
                                                                                                                                                                                    , 7
                                                                                                                                                                                    , 'RDL'
                                                                                                                                                                                    , 8
                                                                                                                                                                                    , 'TSV'
                                                                                                                                                                                    , 9
                                                                                                                                                                                    , 'PKT'
                                                                                                                                                                                    , 10
                                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                                    , 11), REV1) / LAG(NVL(기타재료비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(기타재료비, 0)
                                             END)
                           END) AS 기타재료비
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(노무비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                  , 1
                                                                                                                                                                                  , 'PKG'
                                                                                                                                                                                  , 2
                                                                                                                                                                                  , 'P&T'
                                                                                                                                                                                  , 3
                                                                                                                                                                                  , 'MOD'
                                                                                                                                                                                  , 4
                                                                                                                                                                                  , 'FAB'
                                                                                                                                                                                  , 5
                                                                                                                                                                                  , 'WT'
                                                                                                                                                                                  , 6
                                                                                                                                                                                  , 'ASSY'
                                                                                                                                                                                  , 7
                                                                                                                                                                                  , 'RDL'
                                                                                                                                                                                  , 8
                                                                                                                                                                                  , 'TSV'
                                                                                                                                                                                  , 9
                                                                                                                                                                                  , 'PKT'
                                                                                                                                                                                  , 10
                                                                                                                                                                                  , '생산량(M)'
                                                                                                                                                                                  , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(노무비, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                  , 1
                                                                                                                                                                                  , 'PKG'
                                                                                                                                                                                  , 2
                                                                                                                                                                                  , 'P&T'
                                                                                                                                                                                  , 3
                                                                                                                                                                                  , 'MOD'
                                                                                                                                                                                  , 4
                                                                                                                                                                                  , 'FAB'
                                                                                                                                                                                  , 5
                                                                                                                                                                                  , 'WT'
                                                                                                                                                                                  , 6
                                                                                                                                                                                  , 'ASSY'
                                                                                                                                                                                  , 7
                                                                                                                                                                                  , 'RDL'
                                                                                                                                                                                  , 8
                                                                                                                                                                                  , 'TSV'
                                                                                                                                                                                  , 9
                                                                                                                                                                                  , 'PKT'
                                                                                                                                                                                  , 10
                                                                                                                                                                                  , '생산량(M)'
                                                                                                                                                                                  , 11), REV1) / LAG(NVL(노무비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(노무비, 0)
                                             END)
                           END) AS 노무비
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(기타노무비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                    , 1
                                                                                                                                                                                    , 'PKG'
                                                                                                                                                                                    , 2
                                                                                                                                                                                    , 'P&T'
                                                                                                                                                                                    , 3
                                                                                                                                                                                    , 'MOD'
                                                                                                                                                                                    , 4
                                                                                                                                                                                    , 'FAB'
                                                                                                                                                                                    , 5
                                                                                                                                                                                    , 'WT'
                                                                                                                                                                                    , 6
                                                                                                                                                                                    , 'ASSY'
                                                                                                                                                                                    , 7
                                                                                                                                                                                    , 'RDL'
                                                                                                                                                                                    , 8
                                                                                                                                                                                    , 'TSV'
                                                                                                                                                                                    , 9
                                                                                                                                                                                    , 'PKT'
                                                                                                                                                                                    , 10
                                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                                    , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(기타노무비, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                    , 1
                                                                                                                                                                                    , 'PKG'
                                                                                                                                                                                    , 2
                                                                                                                                                                                    , 'P&T'
                                                                                                                                                                                    , 3
                                                                                                                                                                                    , 'MOD'
                                                                                                                                                                                    , 4
                                                                                                                                                                                    , 'FAB'
                                                                                                                                                                                    , 5
                                                                                                                                                                                    , 'WT'
                                                                                                                                                                                    , 6
                                                                                                                                                                                    , 'ASSY'
                                                                                                                                                                                    , 7
                                                                                                                                                                                    , 'RDL'
                                                                                                                                                                                    , 8
                                                                                                                                                                                    , 'TSV'
                                                                                                                                                                                    , 9
                                                                                                                                                                                    , 'PKT'
                                                                                                                                                                                    , 10
                                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                                    , 11), REV1) / LAG(NVL(기타노무비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(기타노무비, 0)
                                             END)
                           END) AS 기타노무비
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(리스료, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                  , 1
                                                                                                                                                                                  , 'PKG'
                                                                                                                                                                                  , 2
                                                                                                                                                                                  , 'P&T'
                                                                                                                                                                                  , 3
                                                                                                                                                                                  , 'MOD'
                                                                                                                                                                                  , 4
                                                                                                                                                                                  , 'FAB'
                                                                                                                                                                                  , 5
                                                                                                                                                                                  , 'WT'
                                                                                                                                                                                  , 6
                                                                                                                                                                                  , 'ASSY'
                                                                                                                                                                                  , 7
                                                                                                                                                                                  , 'RDL'
                                                                                                                                                                                  , 8
                                                                                                                                                                                  , 'TSV'
                                                                                                                                                                                  , 9
                                                                                                                                                                                  , 'PKT'
                                                                                                                                                                                  , 10
                                                                                                                                                                                  , '생산량(M)'
                                                                                                                                                                                  , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(리스료, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                  , 1
                                                                                                                                                                                  , 'PKG'
                                                                                                                                                                                  , 2
                                                                                                                                                                                  , 'P&T'
                                                                                                                                                                                  , 3
                                                                                                                                                                                  , 'MOD'
                                                                                                                                                                                  , 4
                                                                                                                                                                                  , 'FAB'
                                                                                                                                                                                  , 5
                                                                                                                                                                                  , 'WT'
                                                                                                                                                                                  , 6
                                                                                                                                                                                  , 'ASSY'
                                                                                                                                                                                  , 7
                                                                                                                                                                                  , 'RDL'
                                                                                                                                                                                  , 8
                                                                                                                                                                                  , 'TSV'
                                                                                                                                                                                  , 9
                                                                                                                                                                                  , 'PKT'
                                                                                                                                                                                  , 10
                                                                                                                                                                                  , '생산량(M)'
                                                                                                                                                                                  , 11), REV1) / LAG(NVL(리스료, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(리스료, 0)
                                             END)
                           END) AS 리스료
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(수선비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                  , 1
                                                                                                                                                                                  , 'PKG'
                                                                                                                                                                                  , 2
                                                                                                                                                                                  , 'P&T'
                                                                                                                                                                                  , 3
                                                                                                                                                                                  , 'MOD'
                                                                                                                                                                                  , 4
                                                                                                                                                                                  , 'FAB'
                                                                                                                                                                                  , 5
                                                                                                                                                                                  , 'WT'
                                                                                                                                                                                  , 6
                                                                                                                                                                                  , 'ASSY'
                                                                                                                                                                                  , 7
                                                                                                                                                                                  , 'RDL'
                                                                                                                                                                                  , 8
                                                                                                                                                                                  , 'TSV'
                                                                                                                                                                                  , 9
                                                                                                                                                                                  , 'PKT'
                                                                                                                                                                                  , 10
                                                                                                                                                                                  , '생산량(M)'
                                                                                                                                                                                  , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(수선비, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                  , 1
                                                                                                                                                                                  , 'PKG'
                                                                                                                                                                                  , 2
                                                                                                                                                                                  , 'P&T'
                                                                                                                                                                                  , 3
                                                                                                                                                                                  , 'MOD'
                                                                                                                                                                                  , 4
                                                                                                                                                                                  , 'FAB'
                                                                                                                                                                                  , 5
                                                                                                                                                                                  , 'WT'
                                                                                                                                                                                  , 6
                                                                                                                                                                                  , 'ASSY'
                                                                                                                                                                                  , 7
                                                                                                                                                                                  , 'RDL'
                                                                                                                                                                                  , 8
                                                                                                                                                                                  , 'TSV'
                                                                                                                                                                                  , 9
                                                                                                                                                                                  , 'PKT'
                                                                                                                                                                                  , 10
                                                                                                                                                                                  , '생산량(M)'
                                                                                                                                                                                  , 11), REV1) / LAG(NVL(수선비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(수선비, 0)
                                             END)
                           END) AS 수선비
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(소모품비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                   , 1
                                                                                                                                                                                   , 'PKG'
                                                                                                                                                                                   , 2
                                                                                                                                                                                   , 'P&T'
                                                                                                                                                                                   , 3
                                                                                                                                                                                   , 'MOD'
                                                                                                                                                                                   , 4
                                                                                                                                                                                   , 'FAB'
                                                                                                                                                                                   , 5
                                                                                                                                                                                   , 'WT'
                                                                                                                                                                                   , 6
                                                                                                                                                                                   , 'ASSY'
                                                                                                                                                                                   , 7
                                                                                                                                                                                   , 'RDL'
                                                                                                                                                                                   , 8
                                                                                                                                                                                   , 'TSV'
                                                                                                                                                                                   , 9
                                                                                                                                                                                   , 'PKT'
                                                                                                                                                                                   , 10
                                                                                                                                                                                   , '생산량(M)'
                                                                                                                                                                                   , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(소모품비, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                   , 1
                                                                                                                                                                                   , 'PKG'
                                                                                                                                                                                   , 2
                                                                                                                                                                                   , 'P&T'
                                                                                                                                                                                   , 3
                                                                                                                                                                                   , 'MOD'
                                                                                                                                                                                   , 4
                                                                                                                                                                                   , 'FAB'
                                                                                                                                                                                   , 5
                                                                                                                                                                                   , 'WT'
                                                                                                                                                                                   , 6
                                                                                                                                                                                   , 'ASSY'
                                                                                                                                                                                   , 7
                                                                                                                                                                                   , 'RDL'
                                                                                                                                                                                   , 8
                                                                                                                                                                                   , 'TSV'
                                                                                                                                                                                   , 9
                                                                                                                                                                                   , 'PKT'
                                                                                                                                                                                   , 10
                                                                                                                                                                                   , '생산량(M)'
                                                                                                                                                                                   , 11), REV1) / LAG(NVL(소모품비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(소모품비, 0)
                                             END)
                           END) AS 소모품비
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(UTILITY, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                      , 1
                                                                                                                                                                                      , 'PKG'
                                                                                                                                                                                      , 2
                                                                                                                                                                                      , 'P&T'
                                                                                                                                                                                      , 3
                                                                                                                                                                                      , 'MOD'
                                                                                                                                                                                      , 4
                                                                                                                                                                                      , 'FAB'
                                                                                                                                                                                      , 5
                                                                                                                                                                                      , 'WT'
                                                                                                                                                                                      , 6
                                                                                                                                                                                      , 'ASSY'
                                                                                                                                                                                      , 7
                                                                                                                                                                                      , 'RDL'
                                                                                                                                                                                      , 8
                                                                                                                                                                                      , 'TSV'
                                                                                                                                                                                      , 9
                                                                                                                                                                                      , 'PKT'
                                                                                                                                                                                      , 10
                                                                                                                                                                                      , '생산량(M)'
                                                                                                                                                                                      , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(UTILITY, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                      , 1
                                                                                                                                                                                      , 'PKG'
                                                                                                                                                                                      , 2
                                                                                                                                                                                      , 'P&T'
                                                                                                                                                                                      , 3
                                                                                                                                                                                      , 'MOD'
                                                                                                                                                                                      , 4
                                                                                                                                                                                      , 'FAB'
                                                                                                                                                                                      , 5
                                                                                                                                                                                      , 'WT'
                                                                                                                                                                                      , 6
                                                                                                                                                                                      , 'ASSY'
                                                                                                                                                                                      , 7
                                                                                                                                                                                      , 'RDL'
                                                                                                                                                                                      , 8
                                                                                                                                                                                      , 'TSV'
                                                                                                                                                                                      , 9
                                                                                                                                                                                      , 'PKT'
                                                                                                                                                                                      , 10
                                                                                                                                                                                      , '생산량(M)'
                                                                                                                                                                                      , 11), REV1) / LAG(NVL(UTILITY, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(UTILITY, 0)
                                             END)
                           END) AS UTILITY
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(외주비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                  , 1
                                                                                                                                                                                  , 'PKG'
                                                                                                                                                                                  , 2
                                                                                                                                                                                  , 'P&T'
                                                                                                                                                                                  , 3
                                                                                                                                                                                  , 'MOD'
                                                                                                                                                                                  , 4
                                                                                                                                                                                  , 'FAB'
                                                                                                                                                                                  , 5
                                                                                                                                                                                  , 'WT'
                                                                                                                                                                                  , 6
                                                                                                                                                                                  , 'ASSY'
                                                                                                                                                                                  , 7
                                                                                                                                                                                  , 'RDL'
                                                                                                                                                                                  , 8
                                                                                                                                                                                  , 'TSV'
                                                                                                                                                                                  , 9
                                                                                                                                                                                  , 'PKT'
                                                                                                                                                                                  , 10
                                                                                                                                                                                  , '생산량(M)'
                                                                                                                                                                                  , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(외주비, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                  , 1
                                                                                                                                                                                  , 'PKG'
                                                                                                                                                                                  , 2
                                                                                                                                                                                  , 'P&T'
                                                                                                                                                                                  , 3
                                                                                                                                                                                  , 'MOD'
                                                                                                                                                                                  , 4
                                                                                                                                                                                  , 'FAB'
                                                                                                                                                                                  , 5
                                                                                                                                                                                  , 'WT'
                                                                                                                                                                                  , 6
                                                                                                                                                                                  , 'ASSY'
                                                                                                                                                                                  , 7
                                                                                                                                                                                  , 'RDL'
                                                                                                                                                                                  , 8
                                                                                                                                                                                  , 'TSV'
                                                                                                                                                                                  , 9
                                                                                                                                                                                  , 'PKT'
                                                                                                                                                                                  , 10
                                                                                                                                                                                  , '생산량(M)'
                                                                                                                                                                                  , 11), REV1) / LAG(NVL(외주비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(외주비, 0)
                                             END)
                           END) AS 외주비
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(기타변동비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                    , 1
                                                                                                                                                                                    , 'PKG'
                                                                                                                                                                                    , 2
                                                                                                                                                                                    , 'P&T'
                                                                                                                                                                                    , 3
                                                                                                                                                                                    , 'MOD'
                                                                                                                                                                                    , 4
                                                                                                                                                                                    , 'FAB'
                                                                                                                                                                                    , 5
                                                                                                                                                                                    , 'WT'
                                                                                                                                                                                    , 6
                                                                                                                                                                                    , 'ASSY'
                                                                                                                                                                                    , 7
                                                                                                                                                                                    , 'RDL'
                                                                                                                                                                                    , 8
                                                                                                                                                                                    , 'TSV'
                                                                                                                                                                                    , 9
                                                                                                                                                                                    , 'PKT'
                                                                                                                                                                                    , 10
                                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                                    , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(기타변동비, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                    , 1
                                                                                                                                                                                    , 'PKG'
                                                                                                                                                                                    , 2
                                                                                                                                                                                    , 'P&T'
                                                                                                                                                                                    , 3
                                                                                                                                                                                    , 'MOD'
                                                                                                                                                                                    , 4
                                                                                                                                                                                    , 'FAB'
                                                                                                                                                                                    , 5
                                                                                                                                                                                    , 'WT'
                                                                                                                                                                                    , 6
                                                                                                                                                                                    , 'ASSY'
                                                                                                                                                                                    , 7
                                                                                                                                                                                    , 'RDL'
                                                                                                                                                                                    , 8
                                                                                                                                                                                    , 'TSV'
                                                                                                                                                                                    , 9
                                                                                                                                                                                    , 'PKT'
                                                                                                                                                                                    , 10
                                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                                    , 11), REV1) / LAG(NVL(기타변동비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(기타변동비, 0)
                                             END)
                           END) AS 기타변동비
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(기타고정비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                    , 1
                                                                                                                                                                                    , 'PKG'
                                                                                                                                                                                    , 2
                                                                                                                                                                                    , 'P&T'
                                                                                                                                                                                    , 3
                                                                                                                                                                                    , 'MOD'
                                                                                                                                                                                    , 4
                                                                                                                                                                                    , 'FAB'
                                                                                                                                                                                    , 5
                                                                                                                                                                                    , 'WT'
                                                                                                                                                                                    , 6
                                                                                                                                                                                    , 'ASSY'
                                                                                                                                                                                    , 7
                                                                                                                                                                                    , 'RDL'
                                                                                                                                                                                    , 8
                                                                                                                                                                                    , 'TSV'
                                                                                                                                                                                    , 9
                                                                                                                                                                                    , 'PKT'
                                                                                                                                                                                    , 10
                                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                                    , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(기타고정비, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                    , 1
                                                                                                                                                                                    , 'PKG'
                                                                                                                                                                                    , 2
                                                                                                                                                                                    , 'P&T'
                                                                                                                                                                                    , 3
                                                                                                                                                                                    , 'MOD'
                                                                                                                                                                                    , 4
                                                                                                                                                                                    , 'FAB'
                                                                                                                                                                                    , 5
                                                                                                                                                                                    , 'WT'
                                                                                                                                                                                    , 6
                                                                                                                                                                                    , 'ASSY'
                                                                                                                                                                                    , 7
                                                                                                                                                                                    , 'RDL'
                                                                                                                                                                                    , 8
                                                                                                                                                                                    , 'TSV'
                                                                                                                                                                                    , 9
                                                                                                                                                                                    , 'PKT'
                                                                                                                                                                                    , 10
                                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                                    , 11), REV1) / LAG(NVL(기타고정비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(기타고정비, 0)
                                             END)
                           END) AS 기타고정비
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(감가상각비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                    , 1
                                                                                                                                                                                    , 'PKG'
                                                                                                                                                                                    , 2
                                                                                                                                                                                    , 'P&T'
                                                                                                                                                                                    , 3
                                                                                                                                                                                    , 'MOD'
                                                                                                                                                                                    , 4
                                                                                                                                                                                    , 'FAB'
                                                                                                                                                                                    , 5
                                                                                                                                                                                    , 'WT'
                                                                                                                                                                                    , 6
                                                                                                                                                                                    , 'ASSY'
                                                                                                                                                                                    , 7
                                                                                                                                                                                    , 'RDL'
                                                                                                                                                                                    , 8
                                                                                                                                                                                    , 'TSV'
                                                                                                                                                                                    , 9
                                                                                                                                                                                    , 'PKT'
                                                                                                                                                                                    , 10
                                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                                    , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(감가상각비, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                    , 1
                                                                                                                                                                                    , 'PKG'
                                                                                                                                                                                    , 2
                                                                                                                                                                                    , 'P&T'
                                                                                                                                                                                    , 3
                                                                                                                                                                                    , 'MOD'
                                                                                                                                                                                    , 4
                                                                                                                                                                                    , 'FAB'
                                                                                                                                                                                    , 5
                                                                                                                                                                                    , 'WT'
                                                                                                                                                                                    , 6
                                                                                                                                                                                    , 'ASSY'
                                                                                                                                                                                    , 7
                                                                                                                                                                                    , 'RDL'
                                                                                                                                                                                    , 8
                                                                                                                                                                                    , 'TSV'
                                                                                                                                                                                    , 9
                                                                                                                                                                                    , 'PKT'
                                                                                                                                                                                    , 10
                                                                                                                                                                                    , '생산량(M)'
                                                                                                                                                                                    , 11), REV1) / LAG(NVL(감가상각비, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(감가상각비, 0)
                                             END)
                           END) AS 감가상각비
                         ,(
                           CASE
                                    WHEN MEASURE = '생산량(M)'
                                    THEN NULL
                                    ELSE(
                                             CASE
                                                      WHEN REV1 = 'C'
                                                      THEN((
                                                               CASE
                                                                        WHEN LAG(NVL(TOTAL2, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                     , 1
                                                                                                                                                                                     , 'PKG'
                                                                                                                                                                                     , 2
                                                                                                                                                                                     , 'P&T'
                                                                                                                                                                                     , 3
                                                                                                                                                                                     , 'MOD'
                                                                                                                                                                                     , 4
                                                                                                                                                                                     , 'FAB'
                                                                                                                                                                                     , 5
                                                                                                                                                                                     , 'WT'
                                                                                                                                                                                     , 6
                                                                                                                                                                                     , 'ASSY'
                                                                                                                                                                                     , 7
                                                                                                                                                                                     , 'RDL'
                                                                                                                                                                                     , 8
                                                                                                                                                                                     , 'TSV'
                                                                                                                                                                                     , 9
                                                                                                                                                                                     , 'PKT'
                                                                                                                                                                                     , 10
                                                                                                                                                                                     , '생산량(M)'
                                                                                                                                                                                     , 11), REV1) = 0
                                                                        THEN 0
                                                                        ELSE(LAG(NVL(TOTAL2, 0), 1, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                     , 1
                                                                                                                                                                                     , 'PKG'
                                                                                                                                                                                     , 2
                                                                                                                                                                                     , 'P&T'
                                                                                                                                                                                     , 3
                                                                                                                                                                                     , 'MOD'
                                                                                                                                                                                     , 4
                                                                                                                                                                                     , 'FAB'
                                                                                                                                                                                     , 5
                                                                                                                                                                                     , 'WT'
                                                                                                                                                                                     , 6
                                                                                                                                                                                     , 'ASSY'
                                                                                                                                                                                     , 7
                                                                                                                                                                                     , 'RDL'
                                                                                                                                                                                     , 8
                                                                                                                                                                                     , 'TSV'
                                                                                                                                                                                     , 9
                                                                                                                                                                                     , 'PKT'
                                                                                                                                                                                     , 10
                                                                                                                                                                                     , '생산량(M)'
                                                                                                                                                                                     , 11), REV1) / LAG(NVL(TOTAL2, 0), 2, 0) OVER(ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, DECODE(MEASURE, 'COM'
                                                                                                                                                                                                        , 1
                                                                                                                                                                                                        , 'PKG'
                                                                                                                                                                                                        , 2
                                                                                                                                                                                                        , 'P&T'
                                                                                                                                                                                                        , 3
                                                                                                                                                                                                        , 'MOD'
                                                                                                                                                                                                        , 4
                                                                                                                                                                                                        , 'FAB'
                                                                                                                                                                                                        , 5
                                                                                                                                                                                                        , 'WT'
                                                                                                                                                                                                        , 6
                                                                                                                                                                                                        , 'ASSY'
                                                                                                                                                                                                        , 7
                                                                                                                                                                                                        , 'RDL'
                                                                                                                                                                                                        , 8
                                                                                                                                                                                                        , 'TSV'
                                                                                                                                                                                                        , 9
                                                                                                                                                                                                        , 'PKT'
                                                                                                                                                                                                        , 10
                                                                                                                                                                                                        , '생산량(M)'
                                                                                                                                                                                                        , 11), REV1))
                                                               END) * 100 - 100)
                                                      ELSE NVL(TOTAL2, 0)
                                             END)
                           END) AS TOTAL2
                      FROM(
                                  SELECT A.FAMILY_CD
                                       , A.FAB_ID
                                       , A.TECH_CD
                                       , A.FAB_DEN_CD
                                       , A.CELL_LAYER_TYP_CD
                                       , A.COST_AREA_CD MEASURE
                                       , A.REV REV1
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN ROUND(NVL(M202401, 0), 0)
                                                ELSE NVL(M202401, 0)
                                         END) M202401
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN ROUND(NVL(M202402, 0), 0)
                                                ELSE NVL(M202402, 0)
                                         END) M202402
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN ROUND(NVL(M202403, 0), 0)
                                                ELSE NVL(M202403, 0)
                                         END) M202403
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN ROUND(NVL(M202404, 0), 0)
                                                ELSE NVL(M202404, 0)
                                         END) M202404
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN ROUND(NVL(M202405, 0), 0)
                                                ELSE NVL(M202405, 0)
                                         END) M202405
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN ROUND(NVL(M202406, 0), 0)
                                                ELSE NVL(M202406, 0)
                                         END) M202406
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN ROUND(NVL(M202407, 0), 0)
                                                ELSE NVL(M202407, 0)
                                         END) M202407
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN ROUND(NVL(M202408, 0), 0)
                                                ELSE NVL(M202408, 0)
                                         END) M202408
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN ROUND(NVL(M202409, 0), 0)
                                                ELSE NVL(M202409, 0)
                                         END) M202409
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN ROUND(NVL(M202410, 0), 0)
                                                ELSE NVL(M202410, 0)
                                         END) M202410
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN ROUND(NVL(M202411, 0), 0)
                                                ELSE NVL(M202411, 0)
                                         END) M202411
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN ROUND(NVL(M202412, 0), 0)
                                                ELSE NVL(M202412, 0)
                                         END) M202412
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN ROUND((
                                                       CASE
                                                              WHEN NVL(WAFER, 0) <> 0
                                                              THEN NVL(WAFER, 0)
                                                              WHEN NVL(기타재료비, 0) <> 0
                                                              THEN NVL(기타재료비, 0)
                                                              WHEN NVL(노무비, 0) <> 0
                                                              THEN NVL(노무비, 0)
                                                              WHEN NVL(감가상각비, 0) <> 0
                                                              THEN NVL(감가상각비, 0)
                                                              WHEN NVL(리스료, 0) <> 0
                                                              THEN NVL(리스료, 0)
                                                              WHEN NVL(수선비, 0) <> 0
                                                              THEN NVL(수선비, 0)
                                                              WHEN NVL(소모품비, 0) <> 0
                                                              THEN NVL(소모품비, 0)
                                                              WHEN NVL(UTILITY, 0) <> 0
                                                              THEN NVL(UTILITY, 0)
                                                              WHEN NVL(외주비, 0) <> 0
                                                              THEN NVL(외주비, 0)
                                                              WHEN NVL(기타변동비, 0) <> 0
                                                              THEN NVL(기타변동비, 0)
                                                              WHEN NVL(기타고정비, 0) <> 0
                                                              THEN NVL(기타고정비, 0)
                                                              WHEN NVL(기타노무비, 0) <> 0
                                                              THEN NVL(기타노무비, 0)
                                                              ELSE 0
                                                       END), 0)
                                                ELSE(ROUND((NVL(WAFER, 0) + NVL(기타재료비, 0) + NVL(노무비, 0) + NVL(감가상각비, 0) + NVL(리스료, 0) + NVL(수선비, 0) + NVL(소모품비, 0) + NVL(UTILITY, 0) + NVL(외주비, 0) + NVL(기타변동비, 0) + NVL(기타고정비, 0) + NVL(기타노무비, 0)), 10))
                                         END) 합계
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND((NVL(WAFER, 0) + NVL(기타재료비, 0) + NVL(수선비, 0) + NVL(소모품비, 0) + NVL(UTILITY, 0) *0.8 + NVL(외주비, 0) + NVL(기타변동비, 0)), 10))
                                         END) 변동비
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND((NVL(노무비, 0) + NVL(감가상각비, 0) + NVL(리스료, 0) + NVL(UTILITY, 0) *0.2 + NVL(기타고정비, 0) + NVL(기타노무비, 0)), 10))
                                         END) 고정비
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND(NVL(WAFER, 0) + NVL(기타재료비, 0) + NVL(수선비, 0) + NVL(소모품비, 0) + NVL(UTILITY, 0) * 0.8 + NVL(외주비, 0) + NVL(기타변동비, 0) +(NVL(노무비, 0) + NVL(감가상각비, 0) + NVL(리스료, 0) + NVL(UTILITY, 0) * 0.2 + NVL(기타고정비, 0) + NVL(기타노무비, 0)), 10))
                                         END) TOTAL1
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND(NVL(WAFER, 0), 10))
                                         END) WAFER
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND(NVL(기타재료비, 0), 10))
                                         END) 기타재료비
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND(NVL(노무비, 0), 10))
                                         END) 노무비
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND(NVL(기타노무비, 0), 10))
                                         END) 기타노무비
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND(NVL(리스료, 0), 10))
                                         END) 리스료
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND(NVL(수선비, 0), 10))
                                         END) 수선비
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND(NVL(소모품비, 0), 10))
                                         END) 소모품비
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND(NVL(UTILITY, 0), 10))
                                         END) UTILITY
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND(NVL(외주비, 0), 10))
                                         END) 외주비
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND(NVL(기타변동비, 0), 10))
                                         END) 기타변동비
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND(NVL(기타고정비, 0), 10))
                                         END) 기타고정비
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND(NVL(감가상각비, 0), 10))
                                         END) 감가상각비
                                       ,(
                                         CASE
                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                THEN NULL
                                                ELSE(ROUND(NVL(WAFER, 0) +NVL(기타재료비, 0) +NVL(노무비, 0) +NVL(기타노무비, 0) +NVL(리스료, 0) +NVL(수선비, 0) +NVL(소모품비, 0) +NVL(UTILITY, 0) +NVL(외주비, 0) +NVL(기타변동비, 0) +NVL(기타고정비, 0) +NVL(감가상각비, 0), 10))
                                         END) TOTAL2
                                    FROM(
                                                SELECT A.TGT_YM
                                                     , A.FAMILY_CD
                                                     , A.FAB_ID
                                                     , A.TECH_CD
                                                     , A.FAB_DEN_CD
                                                     , A.CELL_LAYER_TYP_CD
                                                     , A.COST_AREA_CD
                                                     , A.REV
                                                     , A.ASP
                                                  FROM(
                                                              SELECT A.TGT_YM
                                                                   , A.FAMILY_CD
                                                                   , A.FAB_ID
                                                                   , A.TECH_CD
                                                                   , A.FAB_DEN_CD
                                                                   , A.CELL_LAYER_TYP_CD
                                                                   , A.COST_AREA_CD
                                                                   , NVL(A.A_ASP, 0) AS A
                                                                   , NVL(A.B_ASP, 0) AS B
                                                                   , 0               AS C
                                                                FROM(
                                                                                SELECT A.TGT_YM
                                                                                     , A.FAMILY_CD
                                                                                     , A.FAB_ID
                                                                                     , A.TECH_CD
                                                                                     , A.FAB_DEN_CD
                                                                                     , A.CELL_LAYER_TYP_CD
                                                                                     , A.COST_AREA_CD
                                                                                     , A.REV
                                                                                     , NVL((
                                                                                       CASE
                                                                                                WHEN A.COST_AREA_CD = '생산량(M)'
                                                                                                THEN(MAX(NVL(A.COST_QTY, 0)) /1000000)
                                                                                                ELSE(
                                                                                                         CASE
                                                                                                                  WHEN
                                                                                                                           (
                                                                                                                                    MAX(NVL(A.COST_QTY, 0)) <> 0
                                                                                                                           )
                                                                                                                  THEN SUM(NVL(A.COST_AMT, 0)) / MAX(NVL(A.COST_QTY, 0))
                                                                                                                  ELSE 0
                                                                                                         END)
                                                                                       END), 0) AS ASP
                                                                                       /* 계획A 영역 */
                                                                                       /* 년도별 영역 */
                                                                                  FROM(
                                                                                                  SELECT A.COST_PLN_YM
                                                                                                       , A.COST_WEEK_GBN_CD
                                                                                                       , '' PLN_ACTOUT_GBN_CD
                                                                                                       , A.FAMILY_CD
                                                                                                       , A.FAB_ID
                                                                                                       , A.TECH_CD
                                                                                                       , A.FAB_DEN_CD
                                                                                                       , A.CELL_LAYER_TYP_CD
                                                                                                       , A.TGT_YM
                                                                                                       , A.COST_AREA_CD
                                                                                                       , A.REV
                                                                                                       , MAX(B.COST_QTY) COST_QTY
                                                                                                       , SUM(A.COST_AMT) COST_AMT
                                                                                                    FROM(
                                                                                                                  /*실적*/
                                                                                                                    SELECT '202403' COST_PLN_YM
                                                                                                                         , 'W2-SNC-30' COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , A.COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_ACT_1 A
                                                                                                                  GROUP BY '202403'
                                                                                                                         , 'W2-SNC-30'
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                    SELECT '202403' COST_PLN_YM
                                                                                                                         , 'W2-SNC-30' COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , 'COM' COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_ACT_1 A
                                                                                                                  GROUP BY '202403'
                                                                                                                         , 'W2-SNC-30'
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                    SELECT '202403' COST_PLN_YM
                                                                                                                         , 'W2-SNC-30' COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , 'P&T' COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_ACT_1 A
                                                                                                                     WHERE 1=1
                                                                                                                       AND A.COST_AREA_CD IN('WT'
                                                                                                                                           , 'PKT'
                                                                                                                                           , 'MOD'
                                                                                                                                           , 'ASSY'
                                                                                                                                           , 'RDL'
                                                                                                                                           , 'TSV')
                                                                                                                  GROUP BY '202403'
                                                                                                                         , 'W2-SNC-30'
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                    SELECT '202403' COST_PLN_YM
                                                                                                                         , 'W2-SNC-30' COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , 'PKG' COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_ACT_1 A
                                                                                                                     WHERE 1 = 1
                                                                                                                       AND A.COST_AREA_CD IN('ASSY'
                                                                                                                                           , 'RDL'
                                                                                                                                           , 'TSV')
                                                                                                                  GROUP BY '202403'
                                                                                                                         , 'W2-SNC-30'
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                  SELECT '202403' COST_PLN_YM
                                                                                                                       , 'W2-SNC-30' COST_WEEK_GBN_CD
                                                                                                                       , '' PLN_ACTOUT_GBN_CD
                                                                                                                       , A.FAMILY_CD
                                                                                                                       , A.FAB_ID
                                                                                                                       , A.TECH_CD
                                                                                                                       , A.FAB_DEN_CD
                                                                                                                       , A.CELL_LAYER_TYP_CD
                                                                                                                       , A.TGT_YM
                                                                                                                       , '생산량(M)' COST_AREA_CD
                                                                                                                       , 'A' AS REV
                                                                                                                       , 0 COST_QTY
                                                                                                                       , 0 COST_AMT
                                                                                                                    FROM WITH_ACT_1 A

                                                                                                                  UNION ALL

                                                                                                                  /*계획*/
                                                                                                                    SELECT A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , A.COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_PLN_1 A
                                                                                                                  GROUP BY A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                    SELECT A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , 'COM' COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_PLN_1 A
                                                                                                                  GROUP BY A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                    SELECT A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , 'P&T' COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_PLN_1 A
                                                                                                                     WHERE 1 = 1
                                                                                                                       AND A.COST_AREA_CD IN('WT'
                                                                                                                                           , 'PKT'
                                                                                                                                           , 'MOD'
                                                                                                                                           , 'ASSY'
                                                                                                                                           , 'RDL'
                                                                                                                                           , 'TSV')
                                                                                                                  GROUP BY A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                    SELECT A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , 'PKG' COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_PLN_1 A
                                                                                                                     WHERE 1 = 1
                                                                                                                       AND A.COST_AREA_CD IN('ASSY'
                                                                                                                                           , 'RDL'
                                                                                                                                           , 'TSV')
                                                                                                                  GROUP BY A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                  SELECT A.COST_PLN_YM
                                                                                                                       , A.COST_WEEK_GBN_CD
                                                                                                                       , '' PLN_ACTOUT_GBN_CD
                                                                                                                       , A.FAMILY_CD
                                                                                                                       , A.FAB_ID
                                                                                                                       , A.TECH_CD
                                                                                                                       , A.FAB_DEN_CD
                                                                                                                       , A.CELL_LAYER_TYP_CD
                                                                                                                       , A.TGT_YM
                                                                                                                       , '생산량(M)' COST_AREA_CD
                                                                                                                       , 'A' AS REV
                                                                                                                       , 0 COST_QTY
                                                                                                                       , 0 COST_AMT
                                                                                                                    FROM WITH_PLN_1 A
                                                                                                         )
                                                                                                         A
                                                                                                       ,(
                                                                                                                    SELECT A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , A.COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         ,(
                                                                                                                           CASE
                                                                                                                                    WHEN 'Y' = 'N'
                                                                                                                                    THEN SUM(A.COST_QTY   +A.COST_QTY1)
                                                                                                                                    ELSE SUM(A.COST_EQ_QTY+A.COST_EQ_QTY1)
                                                                                                                           END) AS COST_QTY
                                                                                                                         , 0 COST_AMT
                                                                                                                      FROM(
                                                                                                                                  /*실적*/
                                                                                                                                  SELECT '202403' COST_PLN_YM
                                                                                                                                       , 'W2-SNC-30' COST_WEEK_GBN_CD
                                                                                                                                       , '' PLN_ACTOUT_GBN_CD
                                                                                                                                       , A.FAMILY_CD
                                                                                                                                       ,
                                                                                                                                         /* a.rp_cd, */
                                                                                                                                         A.FAB_ID
                                                                                                                                       , A.TECH_CD
                                                                                                                                       , A.FAB_DEN_CD
                                                                                                                                       , A.PROD_MODE_CD
                                                                                                                                       , A.CELL_LAYER_TYP_CD
                                                                                                                                       , A.BIZ_TYP_CD
                                                                                                                                       , A.PKG_TYP_CD2
                                                                                                                                       , A.MOD_TYP_CD
                                                                                                                                       , A.MOD_STRUCT_TYP_CD
                                                                                                                                       , A.GEN_CD
                                                                                                                                       , A.TGT_YM
                                                                                                                                       , A.COST_AREA_CD
                                                                                                                                       , 'A' AS REV
                                                                                                                                       , A.COST_QTY COST_QTY1
                                                                                                                                       , 0 COST_QTY
                                                                                                                                       , A.COST_EQ_QTY COST_EQ_QTY1
                                                                                                                                       , 0 COST_EQ_QTY
                                                                                                                                       , 0 COST_AMT
                                                                                                                                    FROM WITH_ACT_B1 A

                                                                                                                                  UNION ALL

                                                                                                                                  /*계획*/
                                                                                                                                  SELECT A.COST_PLN_YM
                                                                                                                                       , A.COST_WEEK_GBN_CD
                                                                                                                                       , '' PLN_ACTOUT_GBN_CD
                                                                                                                                       , A.FAMILY_CD
                                                                                                                                       ,
                                                                                                                                         /* a.rp_cd, */
                                                                                                                                         A.FAB_ID
                                                                                                                                       , A.TECH_CD
                                                                                                                                       , A.FAB_DEN_CD
                                                                                                                                       , A.PROD_MODE_CD
                                                                                                                                       , A.CELL_LAYER_TYP_CD
                                                                                                                                       , A.BIZ_TYP_CD
                                                                                                                                       , A.PKG_TYP_CD2
                                                                                                                                       , A.MOD_TYP_CD
                                                                                                                                       , A.MOD_STRUCT_TYP_CD
                                                                                                                                       , A.GEN_CD
                                                                                                                                       , A.TGT_YM
                                                                                                                                       , A.COST_AREA_CD
                                                                                                                                       , 'A' AS REV
                                                                                                                                       , 0 COST_QTY1
                                                                                                                                       , A.COST_QTY
                                                                                                                                       , 0 COST_EQ_QTY1
                                                                                                                                       , A.COST_EQ_QTY
                                                                                                                                       , 0 COST_AMT
                                                                                                                                    FROM WITH_PLN_B1 A
                                                                                                                           )
                                                                                                                           A
                                                                                                                     WHERE 1 = 1
                                                                                                                  GROUP BY A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.TGT_YM
                                                                                                                         , A.COST_AREA_CD
                                                                                                         )
                                                                                                         B
                                                                                                   WHERE 1                             =1
                                                                                                     AND A.COST_PLN_YM                 = B.COST_PLN_YM(+)
                                                                                                     AND A.COST_WEEK_GBN_CD            = B.COST_WEEK_GBN_CD(+)
                                                                                                     AND A.FAMILY_CD                   = B.FAMILY_CD(+)
                                                                                                     AND A.TGT_YM                      = B.TGT_YM(+)
                                                                                                     AND A.FAB_ID                      = B.FAB_ID(+)
                                                                                                     AND A.TECH_CD                     = B.TECH_CD(+)
                                                                                                     AND A.FAB_DEN_CD                  = B.FAB_DEN_CD(+)
                                                                                                     AND NVL(A.CELL_LAYER_TYP_CD, '-') = NVL(B.CELL_LAYER_TYP_CD(+), '-')
                                                                                                     AND A.COST_AREA_CD IN('COM'
                                                                                                                         , 'FAB'
                                                                                                                         , 'WT'
                                                                                                                         , 'PKG'
                                                                                                                         , 'PKT'
                                                                                                                         , 'MOD'
                                                                                                                         , '생산량(M)')
                                                                                                GROUP BY A.COST_PLN_YM
                                                                                                       , A.COST_WEEK_GBN_CD
                                                                                                       , A.FAMILY_CD
                                                                                                       , A.FAB_ID
                                                                                                       , A.TECH_CD
                                                                                                       , A.FAB_DEN_CD
                                                                                                       , A.CELL_LAYER_TYP_CD
                                                                                                       , A.TGT_YM
                                                                                                       , A.COST_AREA_CD
                                                                                                       , A.REV

                                                                                                UNION ALL

                                                                                                /* 계정별 영역 */
                                                                                                  SELECT A.COST_PLN_YM
                                                                                                       , A.COST_WEEK_GBN_CD
                                                                                                       , '' PLN_ACTOUT_GBN_CD
                                                                                                       , A.FAMILY_CD
                                                                                                       , A.FAB_ID
                                                                                                       , A.TECH_CD
                                                                                                       , A.FAB_DEN_CD
                                                                                                       , A.CELL_LAYER_TYP_CD
                                                                                                       , A.COST_ACCT_CD TGT_YM
                                                                                                       , A.COST_AREA_CD
                                                                                                       , A.REV
                                                                                                       , MAX(B.COST_QTY) COST_QTY
                                                                                                       , SUM(A.COST_AMT) COST_AMT
                                                                                                    FROM(
                                                                                                                  /*ACTOUT*/
                                                                                                                    SELECT '202403' COST_PLN_YM
                                                                                                                         , 'W2-SNC-30' COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , A.COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_ACT_1 A
                                                                                                                  GROUP BY '202403'
                                                                                                                         , 'W2-SNC-30'
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                    SELECT '202403' COST_PLN_YM
                                                                                                                         , 'W2-SNC-30' COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , 'COM' COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_ACT_1 A
                                                                                                                  GROUP BY '202403'
                                                                                                                         , 'W2-SNC-30'
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                    SELECT '202403' COST_PLN_YM
                                                                                                                         , 'W2-SNC-30' COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , 'P&T' COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_ACT_1 A
                                                                                                                     WHERE 1 = 1
                                                                                                                       AND A.COST_AREA_CD IN('WT'
                                                                                                                                           , 'PKT'
                                                                                                                                           , 'MOD'
                                                                                                                                           , 'ASSY'
                                                                                                                                           , 'RDL'
                                                                                                                                           , 'TSV')
                                                                                                                  GROUP BY '202403'
                                                                                                                         , 'W2-SNC-30'
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                    SELECT '202403' COST_PLN_YM
                                                                                                                         , 'W2-SNC-30' COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , 'PKG' COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_ACT_1 A
                                                                                                                     WHERE 1 = 1
                                                                                                                       AND A.COST_AREA_CD IN('ASSY'
                                                                                                                                           , 'RDL'
                                                                                                                                           , 'TSV')
                                                                                                                  GROUP BY '202403'
                                                                                                                         , 'W2-SNC-30'
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                  SELECT '202403' COST_PLN_YM
                                                                                                                       , 'W2-SNC-30' COST_WEEK_GBN_CD
                                                                                                                       , '' PLN_ACTOUT_GBN_CD
                                                                                                                       , A.FAMILY_CD
                                                                                                                       , A.FAB_ID
                                                                                                                       , A.TECH_CD
                                                                                                                       , A.FAB_DEN_CD
                                                                                                                       , A.CELL_LAYER_TYP_CD
                                                                                                                       , A.COST_ACCT_CD
                                                                                                                       , '생산량(M)' COST_AREA_CD
                                                                                                                       , 'A' AS REV
                                                                                                                       , 0 COST_QTY
                                                                                                                       , 0 COST_AMT
                                                                                                                    FROM WITH_ACT_1 A

                                                                                                                  UNION ALL

                                                                                                                  /*계획*/
                                                                                                                    SELECT A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , A.COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_PLN_1 A
                                                                                                                  GROUP BY A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                    SELECT A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , 'COM' COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_PLN_1 A
                                                                                                                  GROUP BY A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                    SELECT A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , 'P&T' COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_PLN_1 A
                                                                                                                     WHERE 1 = 1
                                                                                                                       AND A.COST_AREA_CD IN('WT'
                                                                                                                                           , 'PKT'
                                                                                                                                           , 'MOD'
                                                                                                                                           , 'ASSY'
                                                                                                                                           , 'RDL'
                                                                                                                                           , 'TSV')
                                                                                                                  GROUP BY A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                    SELECT A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , 'PKG' COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         , 0 COST_QTY
                                                                                                                         , SUM(A.COST_AMT) COST_AMT
                                                                                                                      FROM WITH_PLN_1 A
                                                                                                                     WHERE 1 = 1
                                                                                                                       AND A.COST_AREA_CD IN('ASSY'
                                                                                                                                           , 'RDL'
                                                                                                                                           , 'TSV')
                                                                                                                  GROUP BY A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , A.COST_AREA_CD

                                                                                                                  UNION ALL

                                                                                                                  SELECT A.COST_PLN_YM
                                                                                                                       , A.COST_WEEK_GBN_CD
                                                                                                                       , '' PLN_ACTOUT_GBN_CD
                                                                                                                       , A.FAMILY_CD
                                                                                                                       , A.FAB_ID
                                                                                                                       , A.TECH_CD
                                                                                                                       , A.FAB_DEN_CD
                                                                                                                       , A.CELL_LAYER_TYP_CD
                                                                                                                       , A.COST_ACCT_CD
                                                                                                                       , '생산량(M)' COST_AREA_CD
                                                                                                                       , 'A' AS REV
                                                                                                                       , 0 COST_QTY
                                                                                                                       , 0 COST_AMT
                                                                                                                    FROM WITH_PLN_1 A
                                                                                                         )
                                                                                                         A
                                                                                                       ,(
                                                                                                                    SELECT A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , '' PLN_ACTOUT_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , A.COST_AREA_CD
                                                                                                                         , 'A' AS REV
                                                                                                                         ,(
                                                                                                                           CASE
                                                                                                                                    WHEN 'Y' = 'N'
                                                                                                                                    THEN SUM(A.COST_QTY   +A.COST_QTY1)
                                                                                                                                    ELSE SUM(A.COST_EQ_QTY+A.COST_EQ_QTY1)
                                                                                                                           END) AS COST_QTY
                                                                                                                         , 0 COST_AMT
                                                                                                                      FROM(
                                                                                                                                  /*실적*/
                                                                                                                                  SELECT '202403' COST_PLN_YM
                                                                                                                                       , 'W2-SNC-30' COST_WEEK_GBN_CD
                                                                                                                                       , '' PLN_ACTOUT_GBN_CD
                                                                                                                                       , A.FAMILY_CD
                                                                                                                                       ,
                                                                                                                                         /* a.rp_cd, */
                                                                                                                                         A.FAB_ID
                                                                                                                                       , A.TECH_CD
                                                                                                                                       , A.FAB_DEN_CD
                                                                                                                                       , A.PROD_MODE_CD
                                                                                                                                       , A.CELL_LAYER_TYP_CD
                                                                                                                                       , A.BIZ_TYP_CD
                                                                                                                                       , A.PKG_TYP_CD2
                                                                                                                                       , A.MOD_TYP_CD
                                                                                                                                       , A.MOD_STRUCT_TYP_CD
                                                                                                                                       , A.GEN_CD
                                                                                                                                       , A.COST_ACCT_CD
                                                                                                                                       , A.COST_AREA_CD
                                                                                                                                       , 'A' AS REV
                                                                                                                                       , A.COST_QTY COST_QTY1
                                                                                                                                       , 0 COST_QTY
                                                                                                                                       , A.COST_EQ_QTY COST_EQ_QTY1
                                                                                                                                       , 0 COST_EQ_QTY
                                                                                                                                       , 0 COST_AMT
                                                                                                                                    FROM WITH_ACT_B1 A

                                                                                                                                  UNION ALL

                                                                                                                                  /*계획*/
                                                                                                                                  SELECT A.COST_PLN_YM
                                                                                                                                       , A.COST_WEEK_GBN_CD
                                                                                                                                       , '' PLN_ACTOUT_GBN_CD
                                                                                                                                       , A.FAMILY_CD
                                                                                                                                       ,
                                                                                                                                         /* a.rp_cd, */
                                                                                                                                         A.FAB_ID
                                                                                                                                       , A.TECH_CD
                                                                                                                                       , A.FAB_DEN_CD
                                                                                                                                       , A.PROD_MODE_CD
                                                                                                                                       , A.CELL_LAYER_TYP_CD
                                                                                                                                       , A.BIZ_TYP_CD
                                                                                                                                       , A.PKG_TYP_CD2
                                                                                                                                       , A.MOD_TYP_CD
                                                                                                                                       , A.MOD_STRUCT_TYP_CD
                                                                                                                                       , A.GEN_CD
                                                                                                                                       , A.COST_ACCT_CD
                                                                                                                                       , A.COST_AREA_CD
                                                                                                                                       , 'A' AS REV
                                                                                                                                       , 0 COST_QTY1
                                                                                                                                       , A.COST_QTY
                                                                                                                                       , 0 COST_EQ_QTY1
                                                                                                                                       , A.COST_EQ_QTY
                                                                                                                                       , 0 COST_AMT
                                                                                                                                    FROM WITH_PLN_B1 A
                                                                                                                           )
                                                                                                                           A
                                                                                                                     WHERE 1 = 1
                                                                                                                  GROUP BY A.COST_PLN_YM
                                                                                                                         , A.COST_WEEK_GBN_CD
                                                                                                                         , A.FAMILY_CD
                                                                                                                         , A.FAB_ID
                                                                                                                         , A.TECH_CD
                                                                                                                         , A.FAB_DEN_CD
                                                                                                                         , A.CELL_LAYER_TYP_CD
                                                                                                                         , A.COST_ACCT_CD
                                                                                                                         , A.COST_AREA_CD
                                                                                                         )
                                                                                                         B
                                                                                                   WHERE 1                             =1
                                                                                                     AND A.COST_PLN_YM                 = B.COST_PLN_YM(+)
                                                                                                     AND A.COST_WEEK_GBN_CD            = B.COST_WEEK_GBN_CD(+)
                                                                                                     AND A.FAMILY_CD                   = B.FAMILY_CD(+)
                                                                                                     AND A.FAB_ID                      = B.FAB_ID(+)
                                                                                                     AND A.TECH_CD                     = B.TECH_CD(+)
                                                                                                     AND A.FAB_DEN_CD                  = B.FAB_DEN_CD(+)
                                                                                                     AND NVL(A.CELL_LAYER_TYP_CD, '-') = NVL(B.CELL_LAYER_TYP_CD(+), '-')
                                                                                                     AND A.COST_AREA_CD IN('COM'
                                                                                                                         , 'FAB'
                                                                                                                         , 'WT'
                                                                                                                         , 'PKG'
                                                                                                                         , 'PKT'
                                                                                                                         , 'MOD'
                                                                                                                         , '생산량(M)')
                                                                                                GROUP BY A.COST_PLN_YM
                                                                                                       , A.COST_WEEK_GBN_CD
                                                                                                       , A.FAMILY_CD
                                                                                                       , A.FAB_ID
                                                                                                       , A.TECH_CD
                                                                                                       , A.FAB_DEN_CD
                                                                                                       , A.CELL_LAYER_TYP_CD
                                                                                                       , A.COST_ACCT_CD
                                                                                                       , A.COST_AREA_CD
                                                                                                       , A.REV
                                                                                       )
                                                                                       A
                                                                              GROUP BY A.TGT_YM
                                                                                     , A.FAMILY_CD
                                                                                     , A.FAB_ID
                                                                                     , A.TECH_CD
                                                                                     , A.FAB_DEN_CD
                                                                                     , A.CELL_LAYER_TYP_CD
                                                                                     , A.COST_AREA_CD
                                                                                     , A.REV
                                                                     )
                                                                     PIVOT(SUM(ASP) AS ASP FOR REV IN('A' AS A
                                                                                                    , 'B' AS B)) A
                                                       )
                                                       UNPIVOT(ASP FOR REV IN(A
                                                                            , B
                                                                            , C)) A
                                         )
                                         PIVOT(SUM(ASP) FOR TGT_YM IN('202401' AS M202401
                                                                    , '202402' AS M202402
                                                                    , '202403' AS M202403
                                                                    , '202404' AS M202404
                                                                    , '202405' AS M202405
                                                                    , '202406' AS M202406
                                                                    , '202407' AS M202407
                                                                    , '202408' AS M202408
                                                                    , '202409' AS M202409
                                                                    , '202410' AS M202410
                                                                    , '202411' AS M202411
                                                                    , '202412' AS M202412
                                                                    , 'VVC01'  AS WAFER
                                                                    , 'VVC02'  AS 기타재료비
                                                                    , 'VVC03'  AS 노무비
                                                                    , 'VVC04'  AS 감가상각비
                                                                    , 'VVC05'  AS 리스료
                                                                    , 'VVC06'  AS 수선비
                                                                    , 'VVC07'  AS 소모품비
                                                                    , 'VVC08'  AS UTILITY
                                                                    , 'VVC09'  AS 외주비
                                                                    , 'VVC10'  AS 기타변동비
                                                                    , 'VVC11'  AS 기타고정비
                                                                    , 'VVC12'  AS 기타노무비)) A
                                       , RPI_FAMILY_CD_VW SCM_FAMILY_CD_SORT
                                       , RPI_TECH_CD_VW TECH_CD_SORT
                                       , RPI_FAB_DEN_CD_VW FAB_DEN_CD_SORT
                                       , RPI_CELL_LAYER_TYP_CD_VW CELL_LAYER_TYP_CD_SORT
                                       , RPI_FAB_CD_VW FAB_ID_SORT
                                   WHERE 1                   =1
                                     AND A.FAMILY_CD         = SCM_FAMILY_CD_SORT.SCM_FAMILY_CD(+)
                                     AND SUBSTR(REV, 1, 1)   = 'A'
                                     AND A.FAB_ID            = FAB_ID_SORT.FAB_CD(+)
                                     AND A.TECH_CD           = TECH_CD_SORT.TECH_CD(+)
                                     AND A.FAB_DEN_CD        = FAB_DEN_CD_SORT.FAB_DEN_CD(+)
                                     AND A.CELL_LAYER_TYP_CD = CELL_LAYER_TYP_CD_SORT.CELL_LAYER_TYP_CD(+)
                           )
         )
         A
       , RPI_FAMILY_CD_VW SCM_FAMILY_CD_SORT
       , RPI_TECH_CD_VW TECH_CD_SORT
       , RPI_FAB_DEN_CD_VW FAB_DEN_CD_SORT
       , RPI_CELL_LAYER_TYP_CD_VW CELL_LAYER_TYP_CD_SORT
       , RPI_FAB_CD_VW FAB_ID_SORT
   WHERE 1=1
     AND A.FAMILY_CD IN('DRAM'
                      , 'NAND'
                      , 'Hybrid'
                      , 'SSD')
     AND A.FAMILY_CD         = SCM_FAMILY_CD_SORT.SCM_FAMILY_CD(+)
     AND A.FAB_ID            = FAB_ID_SORT.FAB_CD(+)
     AND A.TECH_CD           = TECH_CD_SORT.TECH_CD(+)
     AND A.FAB_DEN_CD        = FAB_DEN_CD_SORT.FAB_DEN_CD(+)
     AND A.CELL_LAYER_TYP_CD = CELL_LAYER_TYP_CD_SORT.CELL_LAYER_TYP_CD(+)
ORDER BY SCM_FAMILY_CD_SORT.SCM_FAMILY_SEQ ASC
       , FAB_ID_SORT.FAB_SEQ ASC
       , TECH_CD_SORT.TECH_SEQ ASC
       , FAB_DEN_CD_SORT.FAB_DEN_SEQ ASC
       , CELL_LAYER_TYP_CD_SORT.CELL_LAYER_TYP_SEQ ASC
       , DECODE(MEASURE, 'COM'
              , 1
              , 'FAB'
              , 2
              , 'WT'
              , 3
              , 'PKG'
              , 4
              , 'PKT'
              , 5
              , 'MOD'
              , 6
              , '생산량(M)'
              , 7)