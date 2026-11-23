--![2024-04-24 09:38:13.165] [GSCMPRD2] [20240424093812766RRBSE00905GSCMPRD257133] [RBSE00905] [393] [DBSE009.S005](FAILED)
/* Biz: gscm.r.wf.bse.bseb.db.DBSE009.S005 입고DEMAND조회 */
/* IO: 이신형,2020-06-23T10:28:33(이신형,2020-06-11T10:22:41) */
  SELECT
         CASE
                  WHEN GRP_ID = MAX(GRP_ID) OVER(PARTITION BY 1)
                  THEN 3
                  ELSE DENSE_RANK() OVER(PARTITION BY 1 ORDER BY GRP_ID)
         END RK
       , PLN_REV
       , PLN_REV_NM
       , SCM_FAMILY_CD
       , TECH_CD
       , FAB_DEN_CD
       , CHG_PROD_MODE_CD
       , SCM_PROD_VER_CD
       , ORG_SCM_FAMILY_CD
       , PKG_TYP_CD2
       , CHG_BIZ_TYP_CD
       , RP_CD_NM
       , SUM(NVL(M202404_QTY, 0))                                                                                                                                   AS M202404_QTY
       , SUM(NVL(M202405_QTY, 0))                                                                                                                                   AS M202405_QTY
       , SUM(NVL(M202406_QTY, 0))                                                                                                                                   AS M202406_QTY
       , SUM(NVL(M202407_QTY, 0))                                                                                                                                   AS M202407_QTY
       , SUM(NVL(M202408_QTY, 0))                                                                                                                                   AS M202408_QTY
       , SUM(NVL(M202409_QTY, 0))                                                                                                                                   AS M202409_QTY
       , SUM(NVL(M202404_QTY, 0)) +SUM(NVL(M202405_QTY, 0)) +SUM(NVL(M202406_QTY, 0)) +SUM(NVL(M202407_QTY, 0)) +SUM(NVL(M202408_QTY, 0)) +SUM(NVL(M202409_QTY, 0)) AS TOTAL_SUM
    FROM(
                SELECT T1.GRP_ID
                     , T1.PLN_REV
                     , T1.PLN_REV_NM
                     , T1.PLN_REV_SEQ
                     , CASE
                              WHEN T1.SCM_FAMILY_CD IS NULL
                              THEN '0000'
                              ELSE T1.SCM_FAMILY_SEQ
                       END SCM_FAMILY_SEQ
                     , NVL(T1.SCM_FAMILY_CD, ' ') AS SCM_FAMILY_CD
                     , CASE
                              WHEN T1.TECH_CD IS NULL
                              THEN '0000'
                              ELSE T1.TECH_SEQ
                       END TECH_SEQ
                     , NVL(T1.TECH_CD, ' ') AS TECH_CD
                     , CASE
                              WHEN T1.FAB_DEN_CD IS NULL
                              THEN '0000'
                              ELSE T1.FAB_DEN_SEQ
                       END FAB_DEN_SEQ
                     , NVL(T1.FAB_DEN_CD, ' ') AS FAB_DEN_CD
                     , CASE
                              WHEN T1.CHG_PROD_MODE_CD IS NULL
                              THEN 0
                              ELSE T1.CHG_PROD_MODE_SEQ
                       END CHG_PROD_MODE_SEQ
                     , NVL(T1.CHG_PROD_MODE_CD, ' ')  AS CHG_PROD_MODE_CD
                     , NVL(T1.CELL_LAYER_TYP_CD, ' ') AS CELL_LAYER_TYP_CD
                     , NVL(T1.SCM_PROD_VER_CD, ' ')   AS SCM_PROD_VER_CD
                     , NVL(T1.PNT_UNUS_OPER_VAL, ' ') AS PNT_UNUS_OPER_VAL
                     , NVL(T1.FAB_UNUS_OPER_VAL, ' ') AS FAB_UNUS_OPER_VAL
                     , CASE
                              WHEN T1.PKG_TYP_CD2 IS NULL
                              THEN '0000'
                              ELSE T1.PKG_TYP_SEQ2
                       END PKG_TYP_SEQ2
                     , NVL(T1.PKG_TYP_CD2, ' ') AS PKG_TYP_CD2
                       /*,NVL(T1.FAB2_NM, ' ') AS FAB2_NM*/
                     , CASE
                              WHEN T1.RP_CD_NM IS NULL
                              THEN '0000'
                              ELSE T1.RP_SEQ_NM
                       END RP_SEQ_NM
                     , NVL(T1.RP_CD_NM, ' ')           AS RP_CD_NM
                     , NVL(T1.CHG_BIZ_TYP_CD, ' ')     AS CHG_BIZ_TYP_CD
                     , NVL(T1.ORG_SCM_FAMILY_CD, ' ')  AS ORG_SCM_FAMILY_CD
                     , NVL(T1.ORG_SCM_FAMILY_CD2, ' ') AS ORG_SCM_FAMILY_CD2
                     , CASE
                              WHEN T1.DATA_GBN_CD IS NULL
                              THEN 0
                              ELSE T1.DATA_GBN_SEQ
                       END DATA_GBN_SEQ
                     , DECODE(NVL(T1.DATA_GBN_CD, ' '), 'ACTOUT'
                            , '실적'
                            , NVL(T1.DATA_GBN_CD, ' ')) AS DATA_GBN_CD
                     , T1.RP_SOM_CD
                     , T1.TGT_YM
                     , CASE
                              WHEN T2.QTY_GBN = 'Q'
                              THEN T1.DEMAND_QTY
                              WHEN T2.QTY_GBN = 'F'
                              THEN T1.DEMAND_FAB_QTY
                              WHEN T2.QTY_GBN = 'P'
                              THEN T1.DEMAND_PKG_QTY
                              WHEN T2.QTY_GBN = 'E'
                              THEN T1.DEMAND_EQ_QTY
                              ELSE T1.DEMAND_QTY
                       END QTY
                     , NVL(SALES_PROD_ID, ' ')   AS SALES_PROD_ID
                     , NVL(SALES_BATCH_CD, ' ')  AS SALES_BATCH_CD
                     , NVL(SALES_BATCH_ID, ' ')  AS SALES_BATCH_ID
                     , NVL(T1.SSD_MODEL_CD, ' ') AS SSD_MODEL_CD
                     , NVL(T1.MOD_DEN_CD, ' ')   AS MOD_DEN_CD
                  FROM(
                                  SELECT GROUPING_ID(SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD, ORG_SCM_FAMILY_CD, PKG_TYP_CD2, CHG_BIZ_TYP_CD, RP_CD_NM) AS GRP_ID
                                       , PLN_REV
                                       , PLN_REV_NM
                                       , PLN_REV_SEQ
                                       , SCM_FAMILY_SEQ
                                       , SCM_FAMILY_CD
                                       , TECH_SEQ
                                       , TECH_CD
                                       , FAB_DEN_SEQ
                                       , FAB_DEN_CD
                                       , CHG_PROD_MODE_SEQ
                                       , CHG_PROD_MODE_CD
                                       , CELL_LAYER_TYP_CD
                                       , SCM_PROD_VER_CD
                                       , PNT_UNUS_OPER_VAL
                                       , FAB_UNUS_OPER_VAL
                                       , PKG_TYP_SEQ2
                                       , PKG_TYP_CD2
                                         /*,FAB2_NM*/
                                       , RP_SEQ_NM
                                       , RP_CD_NM
                                       , CHG_BIZ_TYP_CD
                                       , ORG_SCM_FAMILY_CD
                                       , ORG_SCM_FAMILY_CD2
                                       , DATA_GBN_SEQ
                                       , DATA_GBN_CD
                                       , RP_SOM_CD
                                       , TGT_YM
                                       , SUM(DEMAND_QTY)     AS DEMAND_QTY
                                       , SUM(DEMAND_FAB_QTY) AS DEMAND_FAB_QTY
                                       , SUM(DEMAND_PKG_QTY) AS DEMAND_PKG_QTY
                                       , SUM(DEMAND_EQ_QTY)  AS DEMAND_EQ_QTY
                                       , SALES_PROD_ID
                                       , SALES_BATCH_CD
                                       , SALES_BATCH_ID
                                       , SSD_MODEL_CD
                                       , MOD_DEN_CD
                                    FROM(
                                                SELECT A.PLN_REV
                                                     , A.PLN_REV_NM
                                                     , A.PLN_REV_SEQ
                                                     , FAMILY_VW.SCM_FAMILY_SEQ
                                                     , A.SCM_FAMILY_CD
                                                     , NVL(TECH_VW.TECH_SEQ, '9999') AS TECH_SEQ
                                                     , B.TECH_CD
                                                     , NVL(FABDEN_VW.FAB_DEN_SEQ, 9999) AS FAB_DEN_SEQ
                                                     , B.FAB_DEN_CD
                                                     , NVL(MODE_VW.SORT_SEQ, 9999) AS CHG_PROD_MODE_SEQ
                                                     , B.CHG_PROD_MODE_CD
                                                     , B.CELL_LAYER_TYP_CD
                                                     , B.SCM_PROD_VER_CD
                                                     , B.PNT_UNUS_OPER_VAL
                                                     , B.FAB_UNUS_OPER_VAL
                                                     , NVL(STACK_VW.STACK_SEQ, '9999') AS PKG_TYP_SEQ2
                                                     , B.PKG_TYP_CD2
                                                       /*,B.FAB2_NM*/
                                                     , NVL(STACK_VW.STACK_SEQ, '9999') AS RP_SEQ_NM
                                                     , B.RP_CD_NM
                                                     , CASE
                                                              WHEN A.DATA_GBN_CD = 'RM'
                                                              THEN 'RM'
                                                              WHEN A.DATA_GBN_CD = 'RT'
                                                              THEN 'RT'
                                                              ELSE B.CHG_BIZ_TYP_CD
                                                       END AS CHG_BIZ_TYP_CD
                                                     , A.ORG_SCM_FAMILY_CD
                                                     , A.ORG_SCM_FAMILY_CD2
                                                     , A.RP_SOM_CD
                                                     , DECODE(A.DATA_GBN_CD, 'DEMAND'
                                                            , 1
                                                            , 'ACTOUT'
                                                            , 2
                                                            , 3) AS DATA_GBN_SEQ
                                                     , A.DATA_GBN_CD
                                                     , A.TGT_YM
                                                     , A.DEMAND_QTY
                                                     , NVL(B.FAB_QTY, 1) * A.DEMAND_QTY AS DEMAND_FAB_QTY
                                                     , 1                 * A.DEMAND_QTY AS DEMAND_PKG_QTY
                                                       /* 단품이라 1로 정의 */
                                                     , NVL(B.EQ_QTY, 1) * A.DEMAND_QTY AS DEMAND_EQ_QTY
                                                     , SALES_PROD_ID
                                                     , SALES_BATCH_CD
                                                     , SALES_BATCH_ID
                                                     , B.SSD_MODEL_CD
                                                     , B.MOD_DEN_CD
                                                  FROM(
                                                              SELECT PLN_REV
                                                                   , PLN_REV_NM
                                                                   , PLN_REV_SEQ
                                                                   , SCM_FAMILY_CD
                                                                   , RP_SOM_CD
                                                                   , ORG_SCM_FAMILY_CD
                                                                   , ORG_SCM_FAMILY_CD2
                                                                   , DATA_GBN_SEQ
                                                                   , DATA_GBN_CD
                                                                   , TGT_YM
                                                                   , DEMAND_QTY
                                                                   , SALES_PROD_ID
                                                                   , SALES_BATCH_CD
                                                                   , SALES_BATCH_ID
                                                                FROM(
                                                                                SELECT 'WF-202417-BSE-01' AS ORG_REV
                                                                                     , 'WF-202417-BSE-01'
                                                                                                || '(A)' AS ORG_REV_NM
                                                                                     , 1                 AS ORG_REV_SEQ
                                                                                     , ''                AS OBJ_REV
                                                                                     , ''
                                                                                                || '(B)' AS OBJ_REV_NM
                                                                                     , 2                 AS OBJ_REV_SEQ
                                                                                     , NULL              AS GAP_REV
                                                                                     , '차이(A-B)'         AS GAP_REV_NM
                                                                                     , 3                 AS GAP_REV_SEQ
                                                                                     , A.SCM_FAMILY_CD
                                                                                     , A.RP_SOM_CD
                                                                                     , A.ORG_SCM_FAMILY_CD
                                                                                     , A.ORG_SCM_FAMILY_CD2
                                                                                     , A.DATA_GBN_SEQ
                                                                                     , A.DATA_GBN_CD
                                                                                     , A.TGT_YM
                                                                                     , NVL(SUM(A.ORG_QTY), 0)                          AS ORG_QTY
                                                                                     , NVL(SUM(A.OBJ_QTY), 0)                          AS OBJ_QTY
                                                                                     , NVL(SUM(A.ORG_QTY), 0) - NVL(SUM(A.OBJ_QTY), 0) AS GAP_QTY
                                                                                     , SALES_PROD_ID
                                                                                     , SALES_BATCH_CD
                                                                                     , SALES_BATCH_ID
                                                                                  FROM(
                                                                                              SELECT SCM_FAMILY_CD
                                                                                                   , RP_SOM_CD
                                                                                                   , ORG_SCM_FAMILY_CD
                                                                                                   , ORG_SCM_FAMILY_CD2
                                                                                                   , DECODE(DATA_GBN_CD, 'DEMAND'
                                                                                                          , 1
                                                                                                          , 'ACTOUT'
                                                                                                          , 2
                                                                                                          , 3) AS DATA_GBN_SEQ
                                                                                                   , DATA_GBN_CD
                                                                                                   , TGT_YM
                                                                                                   , DEMAND_QTY AS ORG_QTY
                                                                                                   , NULL       AS OBJ_QTY
                                                                                                   , SALES_PROD_ID
                                                                                                   , SALES_BATCH_CD
                                                                                                   , SALES_BATCH AS SALES_BATCH_ID
                                                                                                FROM WMI_MI_MG_VW
                                                                                               WHERE PLN_REV = 'WF-202417-BSE-01'
                                                                                                 AND TGT_YM BETWEEN '202404' AND '202409'
                                                                                                 AND SCM_FAMILY_CD NOT IN('OTHERS'
                                                                                                                        , 'Sensors'
                                                                                                                        , 'FOUNDRY')

                                                                                              UNION ALL

                                                                                              SELECT SCM_FAMILY_CD
                                                                                                   , RP_SOM_CD
                                                                                                   , ORG_SCM_FAMILY_CD
                                                                                                   , ORG_SCM_FAMILY_CD2
                                                                                                   , DECODE(DATA_GBN_CD, 'DEMAND'
                                                                                                          , 1
                                                                                                          , 'ACTOUT'
                                                                                                          , 2
                                                                                                          , 3) AS DATA_GBN_SEQ
                                                                                                   , DATA_GBN_CD
                                                                                                   , TGT_YM
                                                                                                   , 0          AS ORG_QTY
                                                                                                   , DEMAND_QTY AS OBJ_QTY
                                                                                                   , SALES_PROD_ID
                                                                                                   , SALES_BATCH_CD
                                                                                                   , SALES_BATCH AS SALES_BATCH_ID
                                                                                                FROM WMI_MI_MG_VW
                                                                                               WHERE PLN_REV = ''
                                                                                                 AND TGT_YM BETWEEN '202404' AND '202409'
                                                                                                 AND SCM_FAMILY_CD NOT IN('OTHERS'
                                                                                                                        , 'Sensors'
                                                                                                                        , 'FOUNDRY')
                                                                                              /*  과거구간 */

                                                                                              UNION ALL

                                                                                              SELECT B.SCM_FAMILY_CD
                                                                                                   , CASE
                                                                                                            WHEN B.RP_SOM_CD LIKE 'LD_512G_Raw NAND%'
                                                                                                            THEN REPLACE(B.RP_SOM_CD, 'Raw NAND', 'SSD')
                                                                                                            ELSE B.RP_SOM_CD
                                                                                                     END                        AS RP_SOM_CD
                                                                                                   , B.SCM_FAMILY_CD            AS ORG_SCM_FAMILY_CD
                                                                                                   , B.SCM_FAMILY_CD            AS ORG_SCM_FAMILY_CD2
                                                                                                   , 1                          AS DATA_GBN_SEQ
                                                                                                   , 'DEMAND'                   AS DATA_GBN_CD
                                                                                                   , SUBSTR(A.GR_NEED_DT, 1, 6) AS TGT_YM
                                                                                                   ,(NVL(A.USE_QTY, 0) *-1)     AS ORG_QTY
                                                                                                   ,(NVL(A.USE_QTY, 0) *-1)     AS OBJ_QTY
                                                                                                   , A.CONV_SALES_PROD_ID       AS SALES_PROD_ID
                                                                                                   , '-'                        AS SALES_BATCH_CD
                                                                                                   , '-'                        AS SALES_BATCH_ID
                                                                                                FROM STI_LPA_IN_PROD_CONV_REQ_M A
                                                                                                   , MDM_SALES_PROD_M B
                                                                                               WHERE 1=1
                                                                                                 AND GUBUN IN('RT_TYPE_01'
                                                                                                            , 'RT_TYPE_07')
                                                                                                 AND A.CONV_SALES_PROD_ID      =B.SALES_PROD_ID
                                                                                                 AND SUBSTR(GR_NEED_DT, 1, 6) >= '202404'
                                                                                                 AND SUBSTR(GR_NEED_DT, 1, 6)  < '202404'

                                                                                              UNION ALL

                                                                                              SELECT B.SCM_FAMILY_CD
                                                                                                   , CASE
                                                                                                            WHEN B.RP_SOM_CD LIKE 'LD_512G_Raw NAND%'
                                                                                                            THEN REPLACE(B.RP_SOM_CD, 'Raw NAND', 'SSD')
                                                                                                            ELSE B.RP_SOM_CD
                                                                                                     END             AS RP_SOM_CD
                                                                                                   , B.SCM_FAMILY_CD AS ORG_SCM_FAMILY_CD
                                                                                                   , B.SCM_FAMILY_CD AS ORG_SCM_FAMILY_CD2
                                                                                                   , 1               AS DATA_GBN_SEQ
                                                                                                   , CASE
                                                                                                            WHEN GUBUN = 'RT_TYPE_01'
                                                                                                            THEN 'RM'
                                                                                                            ELSE 'RT'
                                                                                                     END                        AS DATA_GBN_CD
                                                                                                   , SUBSTR(A.GR_NEED_DT, 1, 6) AS TGT_YM
                                                                                                   ,(NVL(A.USE_QTY, 0))         AS ORG_QTY
                                                                                                   ,(NVL(A.USE_QTY, 0))         AS OBJ_QTY
                                                                                                   , A.CONV_SALES_PROD_ID       AS SALES_PROD_ID
                                                                                                   , '-'                        AS SALES_BATCH_CD
                                                                                                   , '-'                        AS SALES_BATCH_ID
                                                                                                FROM STI_LPA_IN_PROD_CONV_REQ_M A
                                                                                                   , MDM_SALES_PROD_M B
                                                                                               WHERE 1=1
                                                                                                 AND GUBUN IN('RT_TYPE_01'
                                                                                                            , 'RT_TYPE_07')
                                                                                                 AND A.CONV_SALES_PROD_ID      =B.SALES_PROD_ID
                                                                                                 AND SUBSTR(GR_NEED_DT, 1, 6) >= '202404'
                                                                                                 AND SUBSTR(GR_NEED_DT, 1, 6)  < '202404'
                                                                                              /* 주차 계획 구간 */

                                                                                              UNION ALL

                                                                                              SELECT B.SCM_FAMILY_CD
                                                                                                   , CASE
                                                                                                            WHEN B.RP_SOM_CD LIKE 'LD_512G_Raw NAND%'
                                                                                                            THEN REPLACE(B.RP_SOM_CD, 'Raw NAND', 'SSD')
                                                                                                            ELSE B.RP_SOM_CD
                                                                                                     END                        AS RP_SOM_CD
                                                                                                   , B.SCM_FAMILY_CD            AS ORG_SCM_FAMILY_CD
                                                                                                   , B.SCM_FAMILY_CD            AS ORG_SCM_FAMILY_CD2
                                                                                                   , 1                          AS DATA_GBN_SEQ
                                                                                                   , 'DEMAND'                   AS DATA_GBN_CD
                                                                                                   , SUBSTR(A.GR_NEED_DT, 1, 6) AS TGT_YM
                                                                                                   ,(NVL(A.USE_QTY, 0) *-1)     AS ORG_QTY
                                                                                                   ,(NVL(A.USE_QTY, 0) *-1)     AS OBJ_QTY
                                                                                                   , A.CONV_SALES_PROD_ID       AS SALES_PROD_ID
                                                                                                   , '-'                        AS SALES_BATCH_CD
                                                                                                   , '-'                        AS SALES_BATCH_ID
                                                                                                FROM DDP_PROD_CONV_REQ A
                                                                                                   , MDM_SALES_PROD_M B
                                                                                               WHERE 1=1
                                                                                                 AND GUBUN IN('RT_TYPE_01'
                                                                                                            , 'RT_TYPE_07')
                                                                                                 AND A.CONV_SALES_PROD_ID =B.SALES_PROD_ID
                                                                                                 AND SUBSTR(GR_NEED_DT, 1, 6) BETWEEN '202404' AND '202409'

                                                                                              UNION ALL

                                                                                              SELECT B.SCM_FAMILY_CD
                                                                                                   , CASE
                                                                                                            WHEN B.RP_SOM_CD LIKE 'LD_512G_Raw NAND%'
                                                                                                            THEN REPLACE(B.RP_SOM_CD, 'Raw NAND', 'SSD')
                                                                                                            ELSE B.RP_SOM_CD
                                                                                                     END             AS RP_SOM_CD
                                                                                                   , B.SCM_FAMILY_CD AS ORG_SCM_FAMILY_CD
                                                                                                   , B.SCM_FAMILY_CD AS ORG_SCM_FAMILY_CD2
                                                                                                   , 1               AS DATA_GBN_SEQ
                                                                                                   , CASE
                                                                                                            WHEN GUBUN = 'RT_TYPE_01'
                                                                                                            THEN 'RM'
                                                                                                            ELSE 'RT'
                                                                                                     END                        AS DATA_GBN_CD
                                                                                                   , SUBSTR(A.GR_NEED_DT, 1, 6) AS TGT_YM
                                                                                                   ,(NVL(A.USE_QTY, 0))         AS ORG_QTY
                                                                                                   ,(NVL(A.USE_QTY, 0))         AS OBJ_QTY
                                                                                                   , A.CONV_SALES_PROD_ID       AS SALES_PROD_ID
                                                                                                   , '-'                        AS SALES_BATCH_CD
                                                                                                   , '-'                        AS SALES_BATCH_ID
                                                                                                FROM DDP_PROD_CONV_REQ A
                                                                                                   , MDM_SALES_PROD_M B
                                                                                               WHERE 1=1
                                                                                                 AND GUBUN IN('RT_TYPE_01'
                                                                                                            , 'RT_TYPE_07')
                                                                                                 AND A.CONV_SALES_PROD_ID =B.SALES_PROD_ID
                                                                                                 AND SUBSTR(GR_NEED_DT, 1, 6) BETWEEN '202404' AND '202409'
                                                                                       )
                                                                                       A
                                                                              GROUP BY A.TGT_YM
                                                                                     , A.SCM_FAMILY_CD
                                                                                     , A.ORG_SCM_FAMILY_CD
                                                                                     , A.ORG_SCM_FAMILY_CD2
                                                                                     , A.RP_SOM_CD
                                                                                     , A.DATA_GBN_SEQ
                                                                                     , A.DATA_GBN_CD
                                                                                     , A.TGT_YM
                                                                                     , A.SALES_PROD_ID
                                                                                     , A.SALES_BATCH_CD
                                                                                     , A.SALES_BATCH_ID
                                                                     )
                                                                     UNPIVOT((PLN_REV, PLN_REV_NM, PLN_REV_SEQ, DEMAND_QTY) FOR(MEAS) IN((ORG_REV
                                                                                                                                        , ORG_REV_NM
                                                                                                                                        , ORG_REV_SEQ
                                                                                                                                        , ORG_QTY)
                                                                                                                                       ,(OBJ_REV, OBJ_REV_NM, OBJ_REV_SEQ, OBJ_QTY)
                                                                                                                                       ,(GAP_REV, GAP_REV_NM, GAP_REV_SEQ, GAP_QTY)))
                                                       )
                                                       A
                                                       /*,WMI_RP_SOM_CD_VW B*/
                                                       /*환산기준이 단품일 경우.*/
                                                     , RPI_RP_SOM_CD_VW B
                                                       /*환산기준이 제품일 경우.*/
                                                     , RPI_FAMILY_CD_VW FAMILY_VW
                                                     , RPI_TECH_CD_VW TECH_VW
                                                     , RPI_PROD_MODE_CD_VW MODE_VW
                                                     , RPI_FAB_DEN_CD_VW FABDEN_VW
                                                     , RPI_STACK_CD_VW STACK_VW
                                                 WHERE A.SCM_FAMILY_CD = B.SCM_FAMILY_CD (+)
                                                   AND A.RP_SOM_CD     = B.RP_SOM_CD (+)
                                                       /*AND A.ORG_SCM_FAMILY_CD = B.ORG_SCM_FAMILY_CD (+)*/
                                                       /*환산기준이 단품일 경우.*/
                                                   AND B.SCM_FAMILY_CD    = FAMILY_VW.SCM_FAMILY_CD (+)
                                                   AND B.TECH_CD          = TECH_VW.TECH_CD (+)
                                                   AND B.SCM_FAMILY_CD    = MODE_VW.SCM_FAMILY_CD (+)
                                                   AND B.CHG_PROD_MODE_CD = MODE_VW.CHG_PROD_MODE_CD (+)
                                                   AND B.FAB_DEN_CD       = FABDEN_VW.FAB_DEN_CD (+)
                                                   AND B.PKG_TYP_CD2      = STACK_VW.STACK_CD (+)
                                                   AND A.DATA_GBN_CD IN('DEMAND'
                                                                      , 'ACTOUT'
                                                                      , 'RM'
                                                                      , 'RT')
                                                   AND B.SCM_FAMILY_CD IN('DRAM'
                                                                        , 'Hybrid'
                                                                        , 'SSD')
                                                   AND B.CHG_BIZ_TYP_CD NOT IN('NK'
                                                                             , 'LAD1'
                                                                             , 'LAD2')
                                         )
                                   WHERE 1           = 1
                                     AND PLN_REV_SEQ = 1
                                GROUP BY ROLLUP(SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD, ORG_SCM_FAMILY_CD, PKG_TYP_CD2, CHG_BIZ_TYP_CD, RP_CD_NM)
                                       , SCM_FAMILY_SEQ
                                       , TECH_SEQ
                                       , FAB_DEN_SEQ
                                       , CHG_PROD_MODE_SEQ
                                       , PKG_TYP_SEQ2
                                       , RP_SEQ_NM
                                       , PNT_UNUS_OPER_VAL
                                       , FAB_UNUS_OPER_VAL
                                       , 2
                                       , SALES_PROD_ID
                                       , SALES_BATCH_CD
                                       , SALES_BATCH_ID
                                       , SSD_MODEL_CD
                                       , MOD_DEN_CD
                                       , CELL_LAYER_TYP_CD
                                       , ORG_SCM_FAMILY_CD
                                       , DATA_GBN_SEQ
                                       , DATA_GBN_CD
                                       , PLN_REV
                                       , PLN_REV_NM
                                       , PLN_REV_SEQ
                                       , TGT_YM
                                       , RP_SOM_CD
                       )
                       T1
                     ,(
                              SELECT
                                     CASE
                                            WHEN 'N' = 'Y'
                                            THEN 'E'
                                            ELSE
                                                   CASE
                                                          WHEN INSTR_SELF > 0
                                                          THEN 'Q'
                                                          ELSE
                                                                 CASE
                                                                        WHEN INSTR_PKG > 0
                                                                        THEN 'P'
                                                                        ELSE
                                                                               CASE
                                                                                      WHEN INSTR_FAB > 0
                                                                                      THEN 'F'
                                                                                      ELSE 'E'
                                                                               END
                                                                 END
                                                   END
                                     END QTY_GBN
                                   , DIM_CD
                                   , DECI
                                   , RN
                                   , F_RN
                                   , S_RN
                                   , L_RN
                                FROM(
                                            SELECT INSTR(STR_DIM, ',RP_SOM_CD')   + INSTR(STR_DIM, ',RP_CD') + INSTR(STR_DIM, ',RP_CD_NM') + INSTR(STR_DIM, ',MOD_DEN_CD') AS INSTR_SELF
                                                 , INSTR(STR_DIM, ',PKG_TYP_CD2') + INSTR(STR_DIM, ',PKG_DEN_CD')                                                          AS INSTR_PKG
                                                 , INSTR(STR_DIM, ',FAB_DEN_CD')                                                                                           AS INSTR_FAB
                                                 , DIM_CD
                                                 , POWER(2, RN) - 1               AS DECI
                                                 , MAX(RN) OVER(PARTITION BY 1)   AS F_RN
                                                 , MAX(RN-1) OVER(PARTITION BY 1) AS S_RN
                                                 , MIN(RN) OVER(PARTITION BY 1)   AS L_RN
                                                 , RN
                                              FROM(
                                                              SELECT NVL(LENGTH(REGEXP_REPLACE(STR_DIM, '[^,]+', '')), 0) -LEVEL                                                                                                                                 AS RN
                                                                   , REGEXP_SUBSTR(STR_DIM, '[^,]+', 1, LEVEL)                                                                                                                                                   AS DIM_CD
                                                                   , SUBSTR(STR_DIM, 0, NVL(LAG(INSTR(STR_DIM, REGEXP_SUBSTR(STR_DIM, '[^,]+', 1, LEVEL)) -1) OVER(ORDER BY NVL(LENGTH(REGEXP_REPLACE(STR_DIM, '[^,]+', '')), 0) -LEVEL+1) -1, LENGTH(STR_DIM))) AS STR_DIM
                                                                FROM(
                                                                            SELECT ','
                                                                                          || 'SCM_FAMILY_CD,TECH_CD,FAB_DEN_CD,CHG_PROD_MODE_CD,SCM_PROD_VER_CD,ORG_SCM_FAMILY_CD,PKG_TYP_CD2,CHG_BIZ_TYP_CD,RP_CD_NM' AS STR_DIM
                                                                              FROM DUAL
                                                                     )
                                                                     CONNECT BY LEVEL <= NVL(LENGTH(REGEXP_REPLACE(STR_DIM, '[^,]+', '')), 0)
                                                   )
                                     )
                       )
                       T2
                 WHERE T1.GRP_ID = T2.DECI
                   AND T2.RN IN(T2.F_RN
                              , T2.S_RN
                              , T2.L_RN)
         )
         PIVOT(SUM(QTY) AS QTY FOR TGT_YM IN('202404' AS M202404
                                           , '202405' AS M202405
                                           , '202406' AS M202406
                                           , '202407' AS M202407
                                           , '202408' AS M202408
                                           , '202409' AS M202409))
GROUP BY SCM_FAMILY_SEQ
       , SCM_FAMILY_CD
       , TECH_SEQ
       , TECH_CD
       , FAB_DEN_SEQ
       , FAB_DEN_CD
       , CHG_PROD_MODE_SEQ
       , CHG_PROD_MODE_CD
       , SCM_PROD_VER_CD
       , ORG_SCM_FAMILY_CD
       , PKG_TYP_SEQ2
       , PKG_TYP_CD2
       , CHG_BIZ_TYP_CD
       , RP_SEQ_NM
       , RP_CD_NM
       , GRP_ID
       , PLN_REV
       , PLN_REV_NM
       , PLN_REV_SEQ
ORDER BY SCM_FAMILY_SEQ
       , SCM_FAMILY_CD
       , TECH_SEQ
       , TECH_CD
       , RK
       , FAB_DEN_SEQ
       , FAB_DEN_CD
       , CHG_PROD_MODE_SEQ
       , CHG_PROD_MODE_CD
       , SCM_PROD_VER_CD
       , ORG_SCM_FAMILY_CD
       , PKG_TYP_SEQ2
       , PKG_TYP_CD2
       , DECODE(CHG_BIZ_TYP_CD, 'RM'
              , 2
              , 'RT'
              , 3
              , 1)
       , CHG_BIZ_TYP_CD
       , RP_SEQ_NM
       , RP_CD_NM
       , PLN_REV_SEQ
       , PLN_REV
       , PLN_REV_NM