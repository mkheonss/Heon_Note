![2024-08-21 12:35:08.198] [LOCALHOST] [20240821123505155LRMAR00201LOCALHOST00059] [RMAR00201] [2598] [DMAR002.S001](EXECUTED)
/* Biz: gscm.r.is.mar.marb.db.DMAR002.S001  */
/* IO: 김준수,2024-04-04T15:15:04(김준수,2024-04-04T15:15:04) */
/* DIMENSION, PLN_VER, TGT_YM을 그룹으로 판매수량, 판매단가, 판매금액, 재고수량을 조회(원수량, PKG, FAB, EQ별 조회) */
/* 제품조회 */
WITH ORG_SOURCE_WITH AS
(
           SELECT SCM_FAMILY_CD
                , TECH_CD
                , FAB_DEN_CD
                , CHG_PROD_MODE_CD
                , CELL_LAYER_TYP_CD
                , PLN_REV
                , TGT_YM
                , NVL(SUM(SALE_QTY), 0)     AS SALE_QTY
                , NVL(SUM(SALE_PKG_QTY), 0) AS SALE_PKG_QTY
                , NVL(SUM(SALE_FAB_QTY), 0) AS SALE_FAB_QTY
                , NVL(SUM(SALE_EQ_QTY), 0)  AS SALE_EQ_QTY
                , DECODE(NVL(SUM(SALE_QTY), 0), 0
                       , 0
                       , SUM(SALE_AMT) / SUM(SALE_QTY)) AS SALE_ASP
                , DECODE(NVL(SUM(SALE_PKG_QTY), 0), 0
                       , 0
                       , SUM(SALE_AMT) / SUM(SALE_PKG_QTY)) AS SALE_PKG_ASP
                , DECODE(NVL(SUM(SALE_FAB_QTY), 0), 0
                       , 0
                       , SUM(SALE_AMT) / SUM(SALE_FAB_QTY)) AS SALE_FAB_ASP
                , DECODE(NVL(SUM(SALE_EQ_QTY), 0), 0
                       , 0
                       , SUM(SALE_AMT) / SUM(SALE_EQ_QTY)) AS SALE_EQ_ASP
                , NVL(SUM(SALE_AMT), 0)                    AS SALE_AMT
                , NVL(SUM(INV_QTY), 0)                     AS INV_QTY
                , NVL(SUM(INV_PKG_QTY), 0)                 AS INV_PKG_QTY
                , NVL(SUM(INV_FAB_QTY), 0)                 AS INV_FAB_QTY
                , NVL(SUM(INV_EQ_QTY), 0)                  AS INV_EQ_QTY
             FROM(
                         /* 판매실적(메모리) */
                         SELECT T2.SCM_FAMILY_CD
                              , T1.ORG_SCM_FAMILY_CD
                              , T2.TECH_CD
                              , T2.FAB_DEN_CD
                              , T2.CHG_PROD_MODE_CD
                              , T2.CELL_LAYER_TYP_CD
                              , T2.SCM_PROD_VER_CD
                              , T2.PKG_TYP_CD2
                              , T2.CHG_BIZ_TYP_CD
                              , T2.PKG_DEN_CD
                              , T2.MOD_TYP_CD
                              , T2.MOD_STRUCT_TYP_CD
                              , T2.MOD_DEN_CD
                              , T2.FORM_FACTOR_CD
                              , T2.WLP_GBN
                              , T2.RP_CD_NM
                              , T2.PKG_TYP_CD1
                              , T2.BALL_CNT
                              , T2.ORZN_CD
                              , T2.SSD_MODEL_CD
                              , T2.CTRLR_NM
                              , T1.CUST_ID
                              , T1.SMPL_GBN
                              , T4.ECG_NM AS ECG_NM
                              , T1.APP_LVL_1_CD
                              , T3.APP_LVL_1_NM
                              , T5.PLN_REV
                              , T1.TGT_YM
                              , '' DATA_GBN_CD
                              , '*'                           AS REGION_ID
                              , T1.SALE_QTY                   AS SALE_QTY
                              , T1.SALE_QTY * NVL(PKG_QTY, 1) AS SALE_PKG_QTY
                              , T1.SALE_QTY * NVL(FAB_QTY, 1) AS SALE_FAB_QTY
                              , T1.SALE_QTY * NVL(EQ_QTY, 1)  AS SALE_EQ_QTY
                              , T1.SALE_AMT                   AS SALE_AMT
                              , 0                             AS INV_QTY
                              , 0                             AS INV_PKG_QTY
                              , 0                             AS INV_FAB_QTY
                              , 0                             AS INV_EQ_QTY
                           FROM(
                                           SELECT SCM_FAMILY_CD
                                                , SCM_FAMILY_CD AS ORG_SCM_FAMILY_CD
                                                , DECODE(LAP_YN, 'Y'
                                                       , REPLACE(REPLACE(RP_SOM_CD, 'LAD1', 'W'), 'LAD2', 'W')
                                                       , RP_SOM_CD) AS RP_SOM_CD
                                                , CUST_ID
                                                , CASE
                                                           WHEN SMPL_YN = 'Y'
                                                           THEN 'SAMPLE'
                                                           ELSE 'MASS'
                                                  END SMPL_GBN
                                                , APP_LVL_1_CD
                                                , SALE_YM AS TGT_YM
                                                , NVL(SUM(DECODE(LAP_YN, 'Y'
                                                               , 0
                                                               , SALE_QTY)), 0) AS SALE_QTY
                                                , NVL(SUM(SALE_AMT), 0)         AS SALE_AMT
                                                  /* 판매실적정보(제품) */
                                             FROM RPR_SALE_ACTOUT
                                            WHERE SALE_YM    >= '202401'
                                              AND SALE_YM     < '202406'
                                              AND SALE_GBN_CD = 'MONTH_BILL'
                                              AND SCM_FAMILY_CD IN('DRAM'
                                                                 , 'NAND'
                                                                 , 'Hybrid'
                                                                 , 'SSD')
                                              AND
                                                  (
                                                           (
                                                                    CREDIT_YN = 'N'
                                                                AND LAP_YN    = 'N'
                                                                AND LTS_YN    = 'N'
                                                                AND NOMARK_YN = 'N'
                                                                AND LAD_YN    = 'N'
                                                           )
                                                  )
                                              AND SMPL_YN IN('N'
                                                           , 'Y')
                                         GROUP BY SCM_FAMILY_CD
                                                , SCM_FAMILY_CD
                                                , DECODE(LAP_YN, 'Y'
                                                       , REPLACE(REPLACE(RP_SOM_CD, 'LAD1', 'W'), 'LAD2', 'W')
                                                       , RP_SOM_CD)
                                                , CUST_ID
                                                , APP_LVL_1_CD
                                                , SALE_YM
                                                , CASE
                                                           WHEN SMPL_YN = 'Y'
                                                           THEN 'SAMPLE'
                                                           ELSE 'MASS'
                                                  END
                                )
                                T1
                              ,(
                                       SELECT T1.*
                                            , NVL(TSV_GBN_CD, SCM_PKG_TYP_CD4) AS WLP_GBN
                                         FROM RPI_RP_SOM_CD_VW T1
                                )
                                T2
                              , RPI_APP_LVL_1_CD_VW T3
                              , STI_ECG_ALL_VW T4
                              ,(
                                       SELECT 'RP-202406-W2-SNC-54' AS PLN_REV
                                         FROM DUAL
                                              /* UNION ALL                  SELECT 'RP-201909-W4-BSE-01' PLN_REV                    FROM  DUAL */
                                )
                                T5
                          WHERE T2.RP_SOM_CD(+)    = T1.RP_SOM_CD
                            AND T3.APP_LVL_1_CD(+) = T1.APP_LVL_1_CD
                            AND T4.ECG_CD(+)       = T1.CUST_ID

                         UNION ALL

                         /* 재고실적(메모리) */
                         SELECT T2.SCM_FAMILY_CD
                              , T1.ORG_SCM_FAMILY_CD
                              , T2.TECH_CD
                              , T2.FAB_DEN_CD
                              , T2.CHG_PROD_MODE_CD
                              , T2.CELL_LAYER_TYP_CD
                              , T2.SCM_PROD_VER_CD
                              , T2.PKG_TYP_CD2
                              , T2.CHG_BIZ_TYP_CD
                              , T2.PKG_DEN_CD
                              , T2.MOD_TYP_CD
                              , T2.MOD_STRUCT_TYP_CD
                              , T2.MOD_DEN_CD
                              , T2.FORM_FACTOR_CD
                              , T2.WLP_GBN
                              , T2.RP_CD_NM
                              , T2.PKG_TYP_CD1
                              , T2.BALL_CNT
                              , T2.ORZN_CD
                              , T2.SSD_MODEL_CD
                              , T2.CTRLR_NM
                              , T1.CUST_ID
                              , '*'       AS SMPL_GBN
                              , T3.ECG_NM AS ECG_NM
                              , '*'       AS APP_LVL_1_CD
                              , '*'       AS APP_LVL_1_NM
                              , T4.PLN_CD AS PLN_REV
                              , T1.TGT_YM
                              , '' DATA_GBN_CD
                              , '*'                                                  AS REGION_ID
                              , 0                                                    AS SALE_QTY
                              , 0                                                    AS SALE_PKG_QTY
                              , 0                                                    AS SALE_FAB_QTY
                              , 0                                                    AS SALE_EQ_QTY
                              , 0                                                    AS SALE_AMT
                              , T1.BOH_QTY                                           AS INV_QTY
                              , T1.BOH_QTY * NVL(T2.PKG_QTY, 1) * NVL(T2.QTY_CNT, 1) AS INV_PKG_QTY
                              , T1.BOH_QTY * NVL(T2.FAB_QTY, 1) * NVL(T2.QTY_CNT, 1) AS INV_FAB_QTY
                              , T1.BOH_QTY * NVL(T2.EQ_QTY, 1) * NVL(T2.QTY_CNT, 1)  AS INV_EQ_QTY
                           FROM(
                                       SELECT SCM_FAMILY_CD
                                            , ORG_SCM_FAMILY_CD
                                            , RP_SOM_CD
                                            , CUST_ID
                                            , TGT_YM
                                            , BOH_QTY
                                         FROM(
                                                     SELECT SCM_FAMILY_CD AS SCM_FAMILY_CD
                                                          , SCM_FAMILY_CD AS ORG_SCM_FAMILY_CD
                                                          , RP_SOM_CD
                                                          , CUST_ID
                                                          , TO_CHAR(ADD_MONTHS(TO_DATE(BOH_YM
                                                                   || '01', 'YYYYMMDD'), -1), 'YYYYMM') AS TGT_YM
                                                          , BOH_QTY
                                                            /* BOH정보 */
                                                       FROM RPR_BOH
                                                      WHERE BOH_GBN_CD = 'M0'
                                                        AND AVL_YN     = 'Y'
                                                        AND BOH_YM    >= TO_CHAR(ADD_MONTHS(TO_DATE('202401', 'YYYYMM'), 1), 'YYYYMM')
                                                        AND BOH_YM     < TO_CHAR(ADD_MONTHS(TO_DATE('202406', 'YYYYMM'), 1), 'YYYYMM')
                                              )
                                        WHERE 1=1
                                )
                                T1
                              ,(
                                       SELECT RP_SOM_CD
                                            , SCM_FAMILY_CD
                                            , TECH_CD
                                            , FAB_DEN_CD
                                            , CHG_PROD_MODE_CD
                                            , CELL_LAYER_TYP_CD
                                            , SCM_PROD_VER_CD
                                            , PKG_TYP_CD2
                                            , CHG_BIZ_TYP_CD
                                            , PKG_DEN_CD
                                            , MOD_TYP_CD
                                            , MOD_STRUCT_TYP_CD
                                            , MOD_DEN_CD
                                            , FORM_FACTOR_CD
                                            , NVL(TSV_GBN_CD, SCM_PKG_TYP_CD4) AS WLP_GBN
                                            , PKG_QTY
                                            , FAB_QTY
                                            , EQ_QTY
                                            , 1 AS QTY_CNT
                                            , RP_CD_NM
                                            , PKG_TYP_CD1
                                            , BALL_CNT
                                            , ORZN_CD
                                            , SSD_MODEL_CD
                                            , CTRLR_NM
                                         FROM RPI_RP_SOM_CD_VW
                                )
                                T2
                              , STI_ECG_ALL_VW T3
                              ,(
                                       SELECT 'RP-202406-W2-SNC-54' AS PLN_CD
                                         FROM DUAL
                                              /* UNION ALL                  SELECT 'RP-201909-W4-BSE-01' PLN_REV                      FROM  DUAL */
                                )
                                T4
                          WHERE T2.RP_SOM_CD(+) = T1.RP_SOM_CD
                            AND T3.ECG_CD(+)    = T1.CUST_ID
                            AND T2.SCM_FAMILY_CD IN('DRAM'
                                                  , 'NAND'
                                                  , 'Hybrid'
                                                  , 'SSD')

                         UNION ALL

                         /* 계획(메모리) RMA제외 */
                         SELECT T2.SCM_FAMILY_CD AS SCM_FAMILY_CD
                              , T2.SCM_FAMILY_CD AS ORG_SCM_FAMILY_CD
                              , T2.TECH_CD
                              , T2.FAB_DEN_CD
                              , T2.CHG_PROD_MODE_CD
                              , T2.CELL_LAYER_TYP_CD
                              , T2.SCM_PROD_VER_CD
                              , T2.PKG_TYP_CD2
                              , T2.CHG_BIZ_TYP_CD
                              , T2.PKG_DEN_CD
                              , T2.MOD_TYP_CD
                              , T2.MOD_STRUCT_TYP_CD
                              , T2.MOD_DEN_CD
                              , T2.FORM_FACTOR_CD
                              , T2.WLP_GBN
                              , T2.RP_CD_NM
                              , T2.PKG_TYP_CD1
                              , T2.BALL_CNT
                              , T2.ORZN_CD
                              , T2.SSD_MODEL_CD
                              , T2.CTRLR_NM
                              , T1.CUST_ID
                              , CASE
                                       WHEN T1.CUST_ID IN
                                              (
                                                     SELECT GTS_GVAL3
                                                       FROM MAD_GTS
                                                      WHERE SYS_TYP_CD = 'R'
                                                        AND GTS_ID     = 'CODE'
                                                        AND GTS_TYP_CD = 'MASS_SMPL_GBN'
                                                        AND GTS_GVAL1 IN('PAY_SMPL'
                                                                       , 'FOC_SMPL')
                                                        AND GTS_GVAL3 IN('GC20')
                                              )
                                       THEN 'SAMPLE'
                                       ELSE 'MASS'
                                END SMPL_GBN
                              , T5.ECG_NM AS ECG_NM
                              , T1.APP_LVL_1_CD
                              , T3.APP_LVL_1_NM
                              , T1.PLN_REV AS PLN_REV
                              , T1.TGT_YM
                              , '' DATA_GBN_CD
                              , T1.REGION_ID
                              , T1.SALE_QTY
                              , T1.SALE_QTY * NVL(T2.PKG_QTY, 1) AS SALE_PKG_QTY
                              , T1.SALE_QTY * NVL(T2.FAB_QTY, 1) AS SALE_FAB_QTY
                              , T1.SALE_QTY * NVL(T2.EQ_QTY, 1)  AS SALE_EQ_QTY
                              , T1.SALE_AMT
                              , T1.EOH_QTY                      AS INV_QTY
                              , T1.EOH_QTY * NVL(T2.PKG_QTY, 1) AS INV_PKG_QTY
                              , T1.EOH_QTY * NVL(T2.FAB_QTY, 1) AS INV_FAB_QTY
                              , T1.EOH_QTY * NVL(T2.EQ_QTY, 1)  AS INV_EQ_QTY
                           FROM(
                                       SELECT
                                              /*+ ORDERRED USE_HASH(RPO_SALE_PSI) */
                                              PLN_REV
                                            , RP_SOM_CD
                                            , CUST_ID
                                            , APP_LVL_1_CD
                                            , FAB_ID
                                            , REGION_ID
                                            , TGT_YM
                                            , SALE_QTY
                                            , SALE_AMT
                                            , EOH_QTY
                                         FROM RPO_SALE_PSI
                                        WHERE PLN_REV   IN('RP-202406-W2-SNC-54')
                                          AND RP_SOM_CD IN
                                              (
                                                     SELECT
                                                            /*+ UNNEST */
                                                            RP_SOM_CD
                                                       FROM RPI_RP_SOM_CD_VW
                                                      WHERE LNNVL(CHG_BIZ_TYP_CD = 'S')
                                              )
                                          AND TGT_YM >= '202406'
                                          AND TGT_YM <= '202504'
                                          AND
                                              (
                                                     NVL(SALE_QTY, 0) <> 0 OR NVL(SALE_AMT, 0) <> 0 OR NVL(EOH_QTY, 0) <> 0
                                              )
                                )
                                T1
                              ,(
                                       SELECT T1.*
                                            , NVL(TSV_GBN_CD, SCM_PKG_TYP_CD4) AS WLP_GBN
                                         FROM RPI_RP_SOM_CD_VW T1
                                )
                                T2
                              , RPI_APP_LVL_1_CD_VW T3
                              ,(
                                       SELECT PLN_REV
                                            , FAB_ID
                                            , LINE_MIX_CD
                                            , RP_CD
                                            , TGT_YM
                                            , PGD_MFG_RATIO
                                            , LPGD_MFG_RATIO
                                         FROM RPLS_ADM.RPO_MFG_PLN_LPGD_RATE
                                        WHERE PLN_REV IN('RP-202406-W2-SNC-54')
                                          AND LINE_MIX_CD = 'S_FGS'
                                )
                                T4
                              , STI_ECG_ALL_VW T5
                          WHERE T2.RP_SOM_CD(+)    = T1.RP_SOM_CD
                            AND T3.APP_LVL_1_CD(+) = T1.APP_LVL_1_CD
                            AND T4.PLN_REV(+)      = T1.PLN_REV
                            AND T4.RP_CD(+)        = T1.RP_SOM_CD
                            AND T4.TGT_YM(+)       = T1.TGT_YM
                            AND T4.FAB_ID(+)       = T1.FAB_ID
                            AND T5.ECG_CD(+)       = T1.CUST_ID
                  )
            WHERE 1 = 1
                  /* Family, App, Tech, FAB Dens, Mode, Cell, Ver, PKG Dens, Biz.Type, M.Type, M.Config, M.Dens, 구분, RP NM 콤보박스 조회조건 및 'Low Grade 제외' 체크박스 설정 */
              AND NVL(CHG_BIZ_TYP_CD, ' ') NOT IN('NK'
                                                , 'LAD1'
                                                , 'LAD2')
              AND
                  (
                           (
                                    CUST_ID NOT IN('GC20'
                                                 , 'GD75')
                                AND SMPL_GBN = 'MASS'
                           )
                  OR
                           (
                                    CUST_ID IN('GC20') OR SMPL_GBN = 'SAMPLE'
                           )
                  )
         GROUP BY(SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD, CELL_LAYER_TYP_CD, PLN_REV, TGT_YM)
)
/*           DIMENSION의 조합을 체크하여 아래 순서대로 적용(QTY(원수량), PKG_QTY(PKG수량), FAB_QTY(FAB수량), EQ_QTY(EQ수량)을 선택)              1. RP_CD, RP_SOM_CD, MOD_DEN_CD : 원수량            2. PKG_DEN_CD, PKG_TYP_CD2   : PKG수량              3. FAB_DEN_CD, SOM_CD   : FAB수량              4. 그 외       : EQ수량          */
/* DIMENSION에 대한 정렬, DIMENSION의 순서에 따른 (원수량, PKG_QTY, FAB_QTY, EQ_QTY) 적용, Kpcs 및 Mpcs 적용  */
  SELECT DECODE(GROUPING_CNT, 5
              , '0'
              ,(
                       SELECT SCM_FAMILY_SEQ
                         FROM RPI_FAMILY_CD_VW
                        WHERE SCM_FAMILY_CD = T1.SCM_FAMILY_CD
                )
                ) AS FAMILY_CD_SEQ
       , DECODE(GROUPING_CNT, 5
              , 'G-Total(1Gb Eq.)'
              , SCM_FAMILY_CD) AS SCM_FAMILY_CD
       , DECODE(GROUPING_CNT, 5
              , '0'
              ,(
                       SELECT TECH_SEQ
                         FROM RPI_TECH_CD_VW
                        WHERE TECH_CD = T1.TECH_CD
                )
                ) AS TECH_CD_SEQ
       , TECH_CD
       , DECODE(GROUPING_CNT, 5
              , '0'
              ,(
                       SELECT FAB_DEN_SEQ
                         FROM RPI_FAB_DEN_CD_VW
                        WHERE FAB_DEN_CD = T1.FAB_DEN_CD
                )
                ) AS FAB_DEN_CD_SEQ
       , FAB_DEN_CD
       , DECODE(GROUPING_CNT, 5
              , '0'
              ,(
                       SELECT SORT_SEQ
                         FROM RPI_PROD_MODE_CD_VW
                        WHERE SCM_FAMILY_CD    = T1.SCM_FAMILY_CD
                          AND CHG_PROD_MODE_CD = T1.CHG_PROD_MODE_CD
                )
                ) AS CHG_PROD_MODE_CD_SEQ
       , CHG_PROD_MODE_CD
       , DECODE(GROUPING_CNT, 5
              , '0'
              ,(
                       SELECT CELL_LAYER_TYP_SEQ
                         FROM RPI_CELL_LAYER_TYP_CD_VW
                        WHERE CELL_LAYER_TYP_CD = T1.CELL_LAYER_TYP_CD
                )
                ) AS CELL_LAYER_TYP_CD_SEQ
       , CELL_LAYER_TYP_CD
       , GROUPING_CNT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202401_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202401_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202401_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202401_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202401_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202401_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202401_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202401_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202401_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202401_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202401_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202401_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202401_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202401_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202401_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202401_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202401_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202401_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202401_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202401_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202401_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202401_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202401_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202401_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202401_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202401_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202401_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202401_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202401_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202401_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202401_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202401_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202401_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202401_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202401_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202401_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202401_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202401_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202401_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202401_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202401_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202401_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202401_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202401_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202401_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202401_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202401_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202401_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202401_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202401_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202401_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202401_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202401_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202401_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202401_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202401_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202401_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202401_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202401_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202401_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202401_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202401_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202401_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202401_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202402_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202402_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202402_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202402_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202402_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202402_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202402_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202402_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202402_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202402_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202402_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202402_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202402_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202402_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202402_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202402_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202402_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202402_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202402_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202402_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202402_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202402_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202402_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202402_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202402_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202402_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202402_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202402_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202402_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202402_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202402_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202402_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202402_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202402_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202402_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202402_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202402_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202402_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202402_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202402_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202402_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202402_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202402_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202402_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202402_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202402_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202402_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202402_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202402_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202402_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202402_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202402_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202402_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202402_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202402_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202402_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202402_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202402_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202402_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202402_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202402_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202402_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202402_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202402_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202403_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202403_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202403_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202403_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202403_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202403_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202403_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202403_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202403_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202403_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202403_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202403_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202403_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202403_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202403_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202403_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202403_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202403_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202403_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202403_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202403_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202403_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202403_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202403_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202403_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202403_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202403_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202403_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202403_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202403_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202403_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202403_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202403_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202403_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202403_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202403_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202403_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202403_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202403_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202403_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202403_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202403_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202403_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202403_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202403_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202403_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202403_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202403_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202403_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202403_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202403_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202403_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202403_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202403_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202403_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202403_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202403_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202403_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202403_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202403_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202403_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202403_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202403_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202403_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202401_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202401_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202401_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202401_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202401_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202401_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202401_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202401_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202401_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202401_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202401_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202401_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202401_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202401_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202401_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202403_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202401_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202401_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202401_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202401_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202401_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202401_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202401_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202401_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202401_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202401_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202401_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202401_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202401_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202401_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202401_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202403_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(Q202401_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(Q202401_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(Q202401_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(Q202401_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(Q202401_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(Q202401_SALE_AMT / 1000, 1)
         END AS Q202403_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202401_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202401_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202401_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202401_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202401_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202401_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202401_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202401_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202401_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202401_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202401_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202401_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202401_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202401_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202401_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202403_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202404_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202404_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202404_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202404_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202404_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202404_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202404_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202404_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202404_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202404_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202404_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202404_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202404_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202404_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202404_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202404_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202404_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202404_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202404_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202404_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202404_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202404_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202404_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202404_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202404_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202404_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202404_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202404_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202404_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202404_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202404_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202404_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202404_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202404_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202404_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202404_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202404_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202404_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202404_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202404_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202404_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202404_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202404_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202404_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202404_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202404_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202404_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202404_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202404_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202404_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202404_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202404_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202404_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202404_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202404_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202404_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202404_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202404_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202404_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202404_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202404_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202404_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202404_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202404_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202405_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202405_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202405_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202405_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202405_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202405_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202405_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202405_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202405_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202405_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202405_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202405_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202405_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202405_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202405_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202405_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202405_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202405_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202405_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202405_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202405_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202405_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202405_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202405_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202405_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202405_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202405_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202405_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202405_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202405_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202405_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202405_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202405_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202405_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202405_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202405_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202405_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202405_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202405_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202405_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202405_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202405_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202405_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202405_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202405_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202405_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202405_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202405_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202405_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202405_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202405_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202405_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202405_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202405_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202405_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202405_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202405_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202405_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202405_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202405_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202405_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202405_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202405_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202405_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202406_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202406_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202406_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202406_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202406_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202406_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202406_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202406_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202406_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202406_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202406_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202406_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202406_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202406_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202406_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202406_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202406_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202406_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202406_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202406_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202406_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202406_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202406_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202406_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202406_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202406_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202406_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202406_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202406_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202406_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202406_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202406_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202406_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202406_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202406_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202406_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202406_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202406_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202406_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202406_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202406_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202406_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202406_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202406_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202406_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202406_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202406_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202406_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202406_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202406_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202406_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202406_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202406_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202406_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202406_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202406_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202406_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202406_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202406_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202406_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202406_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202406_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202406_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202406_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202402_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202402_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202402_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202402_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202402_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202402_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202402_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202402_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202402_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202402_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202402_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202402_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202402_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202402_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202402_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202406_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202402_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202402_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202402_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202402_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202402_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202402_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202402_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202402_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202402_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202402_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202402_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202402_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202402_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202402_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202402_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202406_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(Q202402_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(Q202402_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(Q202402_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(Q202402_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(Q202402_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(Q202402_SALE_AMT / 1000, 1)
         END AS Q202406_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202402_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202402_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202402_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202402_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202402_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202402_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202402_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202402_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202402_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202402_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202402_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202402_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202402_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202402_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202402_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202406_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(H202401_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(H202401_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(H202401_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(H202401_SALE_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(H202401_SALE_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(H202401_SALE_EQ_QTY / 1000)
         END AS H202406_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(H202401_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(H202401_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(H202401_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(H202401_SALE_EQ_ASP, 3)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(H202401_SALE_EQ_ASP, 3)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(H202401_SALE_EQ_ASP, 3)
         END AS H202406_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(H202401_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(H202401_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(H202401_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(H202401_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(H202401_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(H202401_SALE_AMT / 1000, 1)
         END AS H202406_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(H202401_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(H202401_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(H202401_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(H202401_INV_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(H202401_INV_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(H202401_INV_EQ_QTY / 1000)
         END AS H202406_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202407_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202407_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202407_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202407_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202407_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202407_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202407_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202407_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202407_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202407_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202407_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202407_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202407_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202407_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202407_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202407_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202407_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202407_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202407_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202407_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202407_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202407_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202407_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202407_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202407_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202407_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202407_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202407_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202407_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202407_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202407_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202407_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202407_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202407_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202407_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202407_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202407_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202407_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202407_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202407_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202407_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202407_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202407_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202407_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202407_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202407_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202407_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202407_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202407_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202407_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202407_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202407_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202407_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202407_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202407_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202407_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202407_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202407_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202407_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202407_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202407_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202407_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202407_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202407_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202408_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202408_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202408_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202408_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202408_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202408_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202408_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202408_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202408_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202408_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202408_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202408_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202408_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202408_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202408_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202408_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202408_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202408_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202408_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202408_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202408_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202408_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202408_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202408_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202408_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202408_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202408_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202408_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202408_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202408_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202408_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202408_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202408_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202408_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202408_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202408_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202408_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202408_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202408_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202408_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202408_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202408_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202408_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202408_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202408_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202408_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202408_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202408_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202408_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202408_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202408_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202408_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202408_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202408_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202408_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202408_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202408_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202408_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202408_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202408_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202408_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202408_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202408_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202408_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202409_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202409_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202409_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202409_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202409_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202409_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202409_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202409_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202409_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202409_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202409_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202409_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202409_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202409_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202409_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202409_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202409_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202409_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202409_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202409_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202409_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202409_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202409_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202409_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202409_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202409_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202409_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202409_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202409_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202409_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202409_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202409_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202409_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202409_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202409_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202409_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202409_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202409_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202409_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202409_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202409_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202409_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202409_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202409_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202409_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202409_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202409_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202409_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202409_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202409_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202409_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202409_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202409_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202409_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202409_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202409_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202409_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202409_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202409_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202409_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202409_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202409_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202409_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202409_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202403_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202403_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202403_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202403_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202403_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202403_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202403_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202403_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202403_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202403_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202403_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202403_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202403_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202403_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202403_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202409_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202403_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202403_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202403_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202403_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202403_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202403_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202403_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202403_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202403_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202403_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202403_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202403_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202403_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202403_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202403_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202409_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(Q202403_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(Q202403_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(Q202403_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(Q202403_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(Q202403_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(Q202403_SALE_AMT / 1000, 1)
         END AS Q202409_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202403_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202403_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202403_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202403_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202403_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202403_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202403_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202403_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202403_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202403_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202403_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202403_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202403_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202403_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202403_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202409_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202410_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202410_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202410_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202410_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202410_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202410_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202410_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202410_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202410_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202410_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202410_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202410_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202410_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202410_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202410_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202410_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202410_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202410_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202410_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202410_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202410_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202410_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202410_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202410_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202410_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202410_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202410_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202410_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202410_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202410_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202410_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202410_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202410_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202410_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202410_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202410_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202410_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202410_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202410_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202410_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202410_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202410_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202410_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202410_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202410_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202410_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202410_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202410_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202410_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202410_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202410_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202410_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202410_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202410_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202410_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202410_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202410_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202410_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202410_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202410_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202410_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202410_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202410_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202410_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202411_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202411_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202411_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202411_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202411_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202411_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202411_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202411_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202411_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202411_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202411_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202411_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202411_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202411_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202411_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202411_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202411_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202411_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202411_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202411_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202411_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202411_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202411_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202411_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202411_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202411_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202411_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202411_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202411_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202411_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202411_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202411_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202411_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202411_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202411_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202411_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202411_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202411_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202411_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202411_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202411_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202411_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202411_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202411_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202411_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202411_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202411_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202411_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202411_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202411_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202411_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202411_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202411_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202411_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202411_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202411_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202411_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202411_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202411_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202411_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202411_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202411_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202411_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202411_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202412_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202412_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202412_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202412_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202412_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202412_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202412_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202412_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202412_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202412_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202412_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202412_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202412_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202412_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202412_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202412_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202412_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202412_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202412_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202412_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202412_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202412_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202412_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202412_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202412_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202412_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202412_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202412_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202412_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202412_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202412_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202412_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202412_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202412_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202412_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202412_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202412_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202412_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202412_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202412_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202412_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202412_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202412_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202412_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202412_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202412_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202412_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202412_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202412_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202412_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202412_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202412_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202412_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202412_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202412_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202412_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202412_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202412_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202412_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202412_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202412_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202412_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202412_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202412_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202404_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202404_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202404_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202404_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202404_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202404_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202404_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202404_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202404_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202404_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202404_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202404_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202404_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202404_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202404_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202412_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202404_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202404_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202404_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202404_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202404_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202404_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202404_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202404_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202404_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202404_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202404_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202404_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202404_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202404_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202404_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202412_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(Q202404_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(Q202404_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(Q202404_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(Q202404_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(Q202404_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(Q202404_SALE_AMT / 1000, 1)
         END AS Q202412_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202404_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202404_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202404_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202404_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202404_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202404_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202404_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202404_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202404_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202404_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202404_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202404_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202404_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202404_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202404_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202412_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(H202402_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(H202402_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(H202402_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(H202402_SALE_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(H202402_SALE_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(H202402_SALE_EQ_QTY / 1000)
         END AS H202412_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(H202402_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(H202402_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(H202402_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(H202402_SALE_EQ_ASP, 3)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(H202402_SALE_EQ_ASP, 3)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(H202402_SALE_EQ_ASP, 3)
         END AS H202412_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(H202402_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(H202402_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(H202402_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(H202402_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(H202402_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(H202402_SALE_AMT / 1000, 1)
         END AS H202412_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(H202402_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(H202402_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(H202402_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(H202402_INV_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(H202402_INV_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(H202402_INV_EQ_QTY / 1000)
         END AS H202412_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(Y2024_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(Y2024_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(Y2024_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(Y2024_SALE_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(Y2024_SALE_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(Y2024_SALE_EQ_QTY / 1000)
         END AS Y202412_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(Y2024_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(Y2024_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(Y2024_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(Y2024_SALE_EQ_ASP, 3)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(Y2024_SALE_EQ_ASP, 3)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(Y2024_SALE_EQ_ASP, 3)
         END AS Y202412_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(Y2024_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(Y2024_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(Y2024_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(Y2024_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(Y2024_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(Y2024_SALE_AMT / 1000, 1)
         END AS Y202412_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(Y2024_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(Y2024_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(Y2024_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(Y2024_INV_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(Y2024_INV_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(Y2024_INV_EQ_QTY / 1000)
         END AS Y202412_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202501_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202501_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202501_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202501_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202501_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202501_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202501_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202501_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202501_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202501_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202501_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202501_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202501_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202501_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202501_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202501_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202501_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202501_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202501_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202501_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202501_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202501_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202501_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202501_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202501_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202501_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202501_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202501_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202501_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202501_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202501_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202501_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202501_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202501_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202501_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202501_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202501_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202501_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202501_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202501_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202501_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202501_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202501_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202501_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202501_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202501_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202501_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202501_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202501_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202501_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202501_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202501_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202501_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202501_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202501_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202501_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202501_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202501_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202501_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202501_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202501_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202501_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202501_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202501_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202502_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202502_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202502_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202502_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202502_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202502_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202502_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202502_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202502_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202502_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202502_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202502_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202502_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202502_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202502_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202502_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202502_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202502_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202502_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202502_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202502_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202502_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202502_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202502_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202502_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202502_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202502_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202502_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202502_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202502_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202502_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202502_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202502_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202502_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202502_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202502_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202502_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202502_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202502_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202502_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202502_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202502_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202502_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202502_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202502_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202502_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202502_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202502_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202502_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202502_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202502_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202502_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202502_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202502_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202502_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202502_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202502_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202502_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202502_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202502_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202502_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202502_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202502_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202502_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202503_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202503_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202503_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202503_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202503_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202503_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202503_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202503_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202503_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202503_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202503_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202503_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202503_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202503_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202503_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202503_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202503_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202503_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202503_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202503_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202503_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202503_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202503_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202503_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202503_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202503_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202503_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202503_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202503_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202503_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202503_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202503_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202503_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202503_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202503_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202503_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202503_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202503_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202503_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202503_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202503_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202503_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202503_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202503_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202503_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202503_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202503_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202503_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202503_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202503_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202503_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202503_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202503_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202503_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202503_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202503_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202503_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202503_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202503_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202503_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202503_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202503_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202503_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202503_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202501_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202501_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202501_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202501_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202501_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202501_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202501_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202501_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202501_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202501_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202501_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202501_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202501_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202501_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202501_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202503_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202501_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202501_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202501_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202501_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202501_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202501_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202501_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202501_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202501_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202501_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202501_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202501_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202501_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202501_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202501_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202503_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(Q202501_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(Q202501_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(Q202501_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(Q202501_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(Q202501_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(Q202501_SALE_AMT / 1000, 1)
         END AS Q202503_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202501_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202501_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202501_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202501_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202501_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202501_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202501_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202501_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202501_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202501_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202501_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202501_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202501_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202501_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202501_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202503_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202504_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202504_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202504_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202504_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202504_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202504_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202504_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202504_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202504_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202504_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202504_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202504_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202504_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202504_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202504_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202504_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202504_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202504_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202504_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202504_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202504_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202504_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202504_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202504_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202504_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202504_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202504_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202504_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202504_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(M202504_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202504_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202504_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202504_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202504_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202504_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202504_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202504_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202504_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202504_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202504_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202504_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202504_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202504_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202504_SALE_AMT
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202504_SALE_AMT
                              END) OVER (), 0
                            , 0
                            , ROUND(M202504_SALE_AMT / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202504_SALE_AMT
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202504_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202504_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(M202504_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN M202504_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202504_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(M202504_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN M202504_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202504_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(M202504_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN M202504_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202504_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(M202504_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN M202504_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202504_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(M202504_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN M202504_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS M202504_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202502_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202502_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202502_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202502_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202502_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202502_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202502_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202502_SALE_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202502_SALE_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202502_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202502_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202502_SALE_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202502_SALE_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202502_SALE_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202502_SALE_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202504_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202502_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202502_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202502_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202502_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202502_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202502_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202502_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202502_SALE_FAB_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202502_SALE_FAB_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202502_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202502_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202502_SALE_EQ_ASP
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202502_SALE_EQ_ASP
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202502_SALE_EQ_ASP / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202502_SALE_EQ_ASP
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202504_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(Q202502_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(Q202502_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(Q202502_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(Q202502_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(Q202502_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(Q202502_SALE_AMT / 1000, 1)
         END AS Q202504_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202502_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD), 0
                            , 0
                            , ROUND(Q202502_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 0
                                       THEN Q202502_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD) * 100, 1))
                  WHEN GROUPING_CNT = 1
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202502_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD), 0
                            , 0
                            , ROUND(Q202502_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 1
                                       THEN Q202502_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD) * 100, 1))
                  WHEN GROUPING_CNT = 2
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202502_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD), 0
                            , 0
                            , ROUND(Q202502_INV_FAB_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 2
                                       THEN Q202502_INV_FAB_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD, TECH_CD) * 100, 1))
                  WHEN GROUPING_CNT = 3
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202502_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD), 0
                            , 0
                            , ROUND(Q202502_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 3
                                       THEN Q202502_INV_EQ_QTY
                              END) OVER(PARTITION BY SCM_FAMILY_CD) * 100, 1))
                  WHEN GROUPING_CNT = 4
                  THEN DECODE(SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202502_INV_EQ_QTY
                              END) OVER (), 0
                            , 0
                            , ROUND(Q202502_INV_EQ_QTY / SUM(
                              CASE
                                       WHEN GROUPING_CNT = 4
                                       THEN Q202502_INV_EQ_QTY
                              END) OVER () * 100, 1))
                  WHEN GROUPING_CNT = 5
                  THEN 100
         END AS Q202504_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(H202501_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(H202501_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(H202501_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(H202501_SALE_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(H202501_SALE_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(H202501_SALE_EQ_QTY / 1000)
         END AS H202504_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(H202501_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(H202501_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(H202501_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(H202501_SALE_EQ_ASP, 3)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(H202501_SALE_EQ_ASP, 3)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(H202501_SALE_EQ_ASP, 3)
         END AS H202504_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(H202501_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(H202501_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(H202501_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(H202501_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(H202501_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(H202501_SALE_AMT / 1000, 1)
         END AS H202504_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(H202501_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(H202501_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(H202501_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(H202501_INV_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(H202501_INV_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(H202501_INV_EQ_QTY / 1000)
         END AS H202504_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(Y2025_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(Y2025_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(Y2025_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(Y2025_SALE_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(Y2025_SALE_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(Y2025_SALE_EQ_QTY / 1000)
         END AS Y202504_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(Y2025_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(Y2025_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(Y2025_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(Y2025_SALE_EQ_ASP, 3)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(Y2025_SALE_EQ_ASP, 3)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(Y2025_SALE_EQ_ASP, 3)
         END AS Y202504_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(Y2025_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(Y2025_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(Y2025_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(Y2025_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(Y2025_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(Y2025_SALE_AMT / 1000, 1)
         END AS Y202504_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(Y2025_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(Y2025_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(Y2025_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(Y2025_INV_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(Y2025_INV_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(Y2025_INV_EQ_QTY / 1000)
         END AS Y202504_INV_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(TOTAL_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(TOTAL_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(TOTAL_SALE_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(TOTAL_SALE_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(TOTAL_SALE_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(TOTAL_SALE_EQ_QTY / 1000)
         END AS TOTAL_SALE_QTY
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(TOTAL_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(TOTAL_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(TOTAL_SALE_FAB_ASP, 3)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(TOTAL_SALE_EQ_ASP, 3)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(TOTAL_SALE_EQ_ASP, 3)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(TOTAL_SALE_EQ_ASP, 3)
         END AS TOTAL_SALE_ASP
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(TOTAL_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(TOTAL_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(TOTAL_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(TOTAL_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(TOTAL_SALE_AMT / 1000, 1)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(TOTAL_SALE_AMT / 1000, 1)
         END AS TOTAL_SALE_AMT
       , CASE
                  WHEN GROUPING_CNT = 0
                  THEN ROUND(TOTAL_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 1
                  THEN ROUND(TOTAL_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 2
                  THEN ROUND(TOTAL_INV_FAB_QTY / 1000)
                  WHEN GROUPING_CNT = 3
                  THEN ROUND(TOTAL_INV_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 4
                  THEN ROUND(TOTAL_INV_EQ_QTY / 1000)
                  WHEN GROUPING_CNT = 5
                  THEN ROUND(TOTAL_INV_EQ_QTY / 1000)
         END AS TOTAL_INV_QTY
       , TOTAL_SALE_QTY_CNT
       , TOTAL_SALE_ASP_CNT
       , TOTAL_SALE_AMT_CNT
       , TOTAL_INV_QTY_CNT
       , ROWNUM AS ROW_NUMBER
    FROM(
                    SELECT SCM_FAMILY_CD
                         , TECH_CD
                         , FAB_DEN_CD
                         , CHG_PROD_MODE_CD
                         , CELL_LAYER_TYP_CD
                           /* ,PLN_REV */
                           /* ROLLUP 데이터생성 */
                         , GROUPING(SCM_FAMILY_CD) + GROUPING(TECH_CD) + GROUPING(FAB_DEN_CD) + GROUPING(CHG_PROD_MODE_CD) + GROUPING(CELL_LAYER_TYP_CD) AS GROUPING_CNT
                         , SUM(M202401_SALE_QTY)                                                                                                         AS M202401_SALE_QTY
                         , SUM(M202401_SALE_PKG_QTY)                                                                                                     AS M202401_SALE_PKG_QTY
                         , SUM(M202401_SALE_FAB_QTY)                                                                                                     AS M202401_SALE_FAB_QTY
                         , SUM(M202401_SALE_EQ_QTY)                                                                                                      AS M202401_SALE_EQ_QTY
                         , DECODE(SUM(M202401_SALE_QTY), 0
                                , 0
                                , SUM(M202401_SALE_AMT) / SUM(M202401_SALE_QTY)) AS M202401_SALE_ASP
                         , DECODE(SUM(M202401_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202401_SALE_AMT) / SUM(M202401_SALE_PKG_QTY)) AS M202401_SALE_PKG_ASP
                         , DECODE(SUM(M202401_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202401_SALE_AMT) / SUM(M202401_SALE_FAB_QTY)) AS M202401_SALE_FAB_ASP
                         , DECODE(SUM(M202401_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202401_SALE_AMT) / SUM(M202401_SALE_EQ_QTY)) AS M202401_SALE_EQ_ASP
                         , SUM(M202401_SALE_AMT)                                    AS M202401_SALE_AMT
                         , SUM(M202401_INV_QTY)                                     AS M202401_INV_QTY
                         , SUM(M202401_INV_PKG_QTY)                                 AS M202401_INV_PKG_QTY
                         , SUM(M202401_INV_FAB_QTY)                                 AS M202401_INV_FAB_QTY
                         , SUM(M202401_INV_EQ_QTY)                                  AS M202401_INV_EQ_QTY
                         , SUM(M202402_SALE_QTY)                                    AS M202402_SALE_QTY
                         , SUM(M202402_SALE_PKG_QTY)                                AS M202402_SALE_PKG_QTY
                         , SUM(M202402_SALE_FAB_QTY)                                AS M202402_SALE_FAB_QTY
                         , SUM(M202402_SALE_EQ_QTY)                                 AS M202402_SALE_EQ_QTY
                         , DECODE(SUM(M202402_SALE_QTY), 0
                                , 0
                                , SUM(M202402_SALE_AMT) / SUM(M202402_SALE_QTY)) AS M202402_SALE_ASP
                         , DECODE(SUM(M202402_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202402_SALE_AMT) / SUM(M202402_SALE_PKG_QTY)) AS M202402_SALE_PKG_ASP
                         , DECODE(SUM(M202402_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202402_SALE_AMT) / SUM(M202402_SALE_FAB_QTY)) AS M202402_SALE_FAB_ASP
                         , DECODE(SUM(M202402_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202402_SALE_AMT) / SUM(M202402_SALE_EQ_QTY)) AS M202402_SALE_EQ_ASP
                         , SUM(M202402_SALE_AMT)                                    AS M202402_SALE_AMT
                         , SUM(M202402_INV_QTY)                                     AS M202402_INV_QTY
                         , SUM(M202402_INV_PKG_QTY)                                 AS M202402_INV_PKG_QTY
                         , SUM(M202402_INV_FAB_QTY)                                 AS M202402_INV_FAB_QTY
                         , SUM(M202402_INV_EQ_QTY)                                  AS M202402_INV_EQ_QTY
                         , SUM(M202403_SALE_QTY)                                    AS M202403_SALE_QTY
                         , SUM(M202403_SALE_PKG_QTY)                                AS M202403_SALE_PKG_QTY
                         , SUM(M202403_SALE_FAB_QTY)                                AS M202403_SALE_FAB_QTY
                         , SUM(M202403_SALE_EQ_QTY)                                 AS M202403_SALE_EQ_QTY
                         , DECODE(SUM(M202403_SALE_QTY), 0
                                , 0
                                , SUM(M202403_SALE_AMT) / SUM(M202403_SALE_QTY)) AS M202403_SALE_ASP
                         , DECODE(SUM(M202403_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202403_SALE_AMT) / SUM(M202403_SALE_PKG_QTY)) AS M202403_SALE_PKG_ASP
                         , DECODE(SUM(M202403_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202403_SALE_AMT) / SUM(M202403_SALE_FAB_QTY)) AS M202403_SALE_FAB_ASP
                         , DECODE(SUM(M202403_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202403_SALE_AMT) / SUM(M202403_SALE_EQ_QTY)) AS M202403_SALE_EQ_ASP
                         , SUM(M202403_SALE_AMT)                                    AS M202403_SALE_AMT
                         , SUM(M202403_INV_QTY)                                     AS M202403_INV_QTY
                         , SUM(M202403_INV_PKG_QTY)                                 AS M202403_INV_PKG_QTY
                         , SUM(M202403_INV_FAB_QTY)                                 AS M202403_INV_FAB_QTY
                         , SUM(M202403_INV_EQ_QTY)                                  AS M202403_INV_EQ_QTY
                         , SUM(Q202401_SALE_QTY)                                    AS Q202401_SALE_QTY
                         , SUM(Q202401_SALE_PKG_QTY)                                AS Q202401_SALE_PKG_QTY
                         , SUM(Q202401_SALE_FAB_QTY)                                AS Q202401_SALE_FAB_QTY
                         , SUM(Q202401_SALE_EQ_QTY)                                 AS Q202401_SALE_EQ_QTY
                         , SUM(Q202401_SALE_AMT)                                    AS Q202401_SALE_AMT
                         , DECODE(SUM(Q202401_SALE_QTY), 0
                                , 0
                                , SUM(Q202401_SALE_AMT) / SUM(Q202401_SALE_QTY)) AS Q202401_SALE_ASP
                         , DECODE(SUM(Q202401_SALE_PKG_QTY), 0
                                , 0
                                , SUM(Q202401_SALE_AMT) / SUM(Q202401_SALE_PKG_QTY)) AS Q202401_SALE_PKG_ASP
                         , DECODE(SUM(Q202401_SALE_FAB_QTY), 0
                                , 0
                                , SUM(Q202401_SALE_AMT) / SUM(Q202401_SALE_FAB_QTY)) AS Q202401_SALE_FAB_ASP
                         , DECODE(SUM(Q202401_SALE_EQ_QTY), 0
                                , 0
                                , SUM(Q202401_SALE_AMT) / SUM(Q202401_SALE_EQ_QTY)) AS Q202401_SALE_EQ_ASP
                         , SUM(Q202401_INV_QTY)                                     AS Q202401_INV_QTY
                         , SUM(Q202401_INV_PKG_QTY)                                 AS Q202401_INV_PKG_QTY
                         , SUM(Q202401_INV_FAB_QTY)                                 AS Q202401_INV_FAB_QTY
                         , SUM(Q202401_INV_EQ_QTY)                                  AS Q202401_INV_EQ_QTY
                         , SUM(M202404_SALE_QTY)                                    AS M202404_SALE_QTY
                         , SUM(M202404_SALE_PKG_QTY)                                AS M202404_SALE_PKG_QTY
                         , SUM(M202404_SALE_FAB_QTY)                                AS M202404_SALE_FAB_QTY
                         , SUM(M202404_SALE_EQ_QTY)                                 AS M202404_SALE_EQ_QTY
                         , DECODE(SUM(M202404_SALE_QTY), 0
                                , 0
                                , SUM(M202404_SALE_AMT) / SUM(M202404_SALE_QTY)) AS M202404_SALE_ASP
                         , DECODE(SUM(M202404_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202404_SALE_AMT) / SUM(M202404_SALE_PKG_QTY)) AS M202404_SALE_PKG_ASP
                         , DECODE(SUM(M202404_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202404_SALE_AMT) / SUM(M202404_SALE_FAB_QTY)) AS M202404_SALE_FAB_ASP
                         , DECODE(SUM(M202404_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202404_SALE_AMT) / SUM(M202404_SALE_EQ_QTY)) AS M202404_SALE_EQ_ASP
                         , SUM(M202404_SALE_AMT)                                    AS M202404_SALE_AMT
                         , SUM(M202404_INV_QTY)                                     AS M202404_INV_QTY
                         , SUM(M202404_INV_PKG_QTY)                                 AS M202404_INV_PKG_QTY
                         , SUM(M202404_INV_FAB_QTY)                                 AS M202404_INV_FAB_QTY
                         , SUM(M202404_INV_EQ_QTY)                                  AS M202404_INV_EQ_QTY
                         , SUM(M202405_SALE_QTY)                                    AS M202405_SALE_QTY
                         , SUM(M202405_SALE_PKG_QTY)                                AS M202405_SALE_PKG_QTY
                         , SUM(M202405_SALE_FAB_QTY)                                AS M202405_SALE_FAB_QTY
                         , SUM(M202405_SALE_EQ_QTY)                                 AS M202405_SALE_EQ_QTY
                         , DECODE(SUM(M202405_SALE_QTY), 0
                                , 0
                                , SUM(M202405_SALE_AMT) / SUM(M202405_SALE_QTY)) AS M202405_SALE_ASP
                         , DECODE(SUM(M202405_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202405_SALE_AMT) / SUM(M202405_SALE_PKG_QTY)) AS M202405_SALE_PKG_ASP
                         , DECODE(SUM(M202405_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202405_SALE_AMT) / SUM(M202405_SALE_FAB_QTY)) AS M202405_SALE_FAB_ASP
                         , DECODE(SUM(M202405_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202405_SALE_AMT) / SUM(M202405_SALE_EQ_QTY)) AS M202405_SALE_EQ_ASP
                         , SUM(M202405_SALE_AMT)                                    AS M202405_SALE_AMT
                         , SUM(M202405_INV_QTY)                                     AS M202405_INV_QTY
                         , SUM(M202405_INV_PKG_QTY)                                 AS M202405_INV_PKG_QTY
                         , SUM(M202405_INV_FAB_QTY)                                 AS M202405_INV_FAB_QTY
                         , SUM(M202405_INV_EQ_QTY)                                  AS M202405_INV_EQ_QTY
                         , SUM(M202406_SALE_QTY)                                    AS M202406_SALE_QTY
                         , SUM(M202406_SALE_PKG_QTY)                                AS M202406_SALE_PKG_QTY
                         , SUM(M202406_SALE_FAB_QTY)                                AS M202406_SALE_FAB_QTY
                         , SUM(M202406_SALE_EQ_QTY)                                 AS M202406_SALE_EQ_QTY
                         , DECODE(SUM(M202406_SALE_QTY), 0
                                , 0
                                , SUM(M202406_SALE_AMT) / SUM(M202406_SALE_QTY)) AS M202406_SALE_ASP
                         , DECODE(SUM(M202406_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202406_SALE_AMT) / SUM(M202406_SALE_PKG_QTY)) AS M202406_SALE_PKG_ASP
                         , DECODE(SUM(M202406_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202406_SALE_AMT) / SUM(M202406_SALE_FAB_QTY)) AS M202406_SALE_FAB_ASP
                         , DECODE(SUM(M202406_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202406_SALE_AMT) / SUM(M202406_SALE_EQ_QTY)) AS M202406_SALE_EQ_ASP
                         , SUM(M202406_SALE_AMT)                                    AS M202406_SALE_AMT
                         , SUM(M202406_INV_QTY)                                     AS M202406_INV_QTY
                         , SUM(M202406_INV_PKG_QTY)                                 AS M202406_INV_PKG_QTY
                         , SUM(M202406_INV_FAB_QTY)                                 AS M202406_INV_FAB_QTY
                         , SUM(M202406_INV_EQ_QTY)                                  AS M202406_INV_EQ_QTY
                         , SUM(Q202402_SALE_QTY)                                    AS Q202402_SALE_QTY
                         , SUM(Q202402_SALE_PKG_QTY)                                AS Q202402_SALE_PKG_QTY
                         , SUM(Q202402_SALE_FAB_QTY)                                AS Q202402_SALE_FAB_QTY
                         , SUM(Q202402_SALE_EQ_QTY)                                 AS Q202402_SALE_EQ_QTY
                         , SUM(Q202402_SALE_AMT)                                    AS Q202402_SALE_AMT
                         , DECODE(SUM(Q202402_SALE_QTY), 0
                                , 0
                                , SUM(Q202402_SALE_AMT) / SUM(Q202402_SALE_QTY)) AS Q202402_SALE_ASP
                         , DECODE(SUM(Q202402_SALE_PKG_QTY), 0
                                , 0
                                , SUM(Q202402_SALE_AMT) / SUM(Q202402_SALE_PKG_QTY)) AS Q202402_SALE_PKG_ASP
                         , DECODE(SUM(Q202402_SALE_FAB_QTY), 0
                                , 0
                                , SUM(Q202402_SALE_AMT) / SUM(Q202402_SALE_FAB_QTY)) AS Q202402_SALE_FAB_ASP
                         , DECODE(SUM(Q202402_SALE_EQ_QTY), 0
                                , 0
                                , SUM(Q202402_SALE_AMT) / SUM(Q202402_SALE_EQ_QTY)) AS Q202402_SALE_EQ_ASP
                         , SUM(Q202402_INV_QTY)                                     AS Q202402_INV_QTY
                         , SUM(Q202402_INV_PKG_QTY)                                 AS Q202402_INV_PKG_QTY
                         , SUM(Q202402_INV_FAB_QTY)                                 AS Q202402_INV_FAB_QTY
                         , SUM(Q202402_INV_EQ_QTY)                                  AS Q202402_INV_EQ_QTY
                         , SUM(H202401_SALE_QTY)                                    AS H202401_SALE_QTY
                         , SUM(H202401_SALE_PKG_QTY)                                AS H202401_SALE_PKG_QTY
                         , SUM(H202401_SALE_FAB_QTY)                                AS H202401_SALE_FAB_QTY
                         , SUM(H202401_SALE_EQ_QTY)                                 AS H202401_SALE_EQ_QTY
                         , SUM(H202401_SALE_AMT)                                    AS H202401_SALE_AMT
                         , DECODE(SUM(H202401_SALE_QTY), 0
                                , 0
                                , SUM(H202401_SALE_AMT) / SUM(H202401_SALE_QTY)) AS H202401_SALE_ASP
                         , DECODE(SUM(H202401_SALE_PKG_QTY), 0
                                , 0
                                , SUM(H202401_SALE_AMT) / SUM(H202401_SALE_PKG_QTY)) AS H202401_SALE_PKG_ASP
                         , DECODE(SUM(H202401_SALE_FAB_QTY), 0
                                , 0
                                , SUM(H202401_SALE_AMT) / SUM(H202401_SALE_FAB_QTY)) AS H202401_SALE_FAB_ASP
                         , DECODE(SUM(H202401_SALE_EQ_QTY), 0
                                , 0
                                , SUM(H202401_SALE_AMT) / SUM(H202401_SALE_EQ_QTY)) AS H202401_SALE_EQ_ASP
                         , SUM(H202401_INV_QTY)                                     AS H202401_INV_QTY
                         , SUM(H202401_INV_PKG_QTY)                                 AS H202401_INV_PKG_QTY
                         , SUM(H202401_INV_FAB_QTY)                                 AS H202401_INV_FAB_QTY
                         , SUM(H202401_INV_EQ_QTY)                                  AS H202401_INV_EQ_QTY
                         , SUM(M202407_SALE_QTY)                                    AS M202407_SALE_QTY
                         , SUM(M202407_SALE_PKG_QTY)                                AS M202407_SALE_PKG_QTY
                         , SUM(M202407_SALE_FAB_QTY)                                AS M202407_SALE_FAB_QTY
                         , SUM(M202407_SALE_EQ_QTY)                                 AS M202407_SALE_EQ_QTY
                         , DECODE(SUM(M202407_SALE_QTY), 0
                                , 0
                                , SUM(M202407_SALE_AMT) / SUM(M202407_SALE_QTY)) AS M202407_SALE_ASP
                         , DECODE(SUM(M202407_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202407_SALE_AMT) / SUM(M202407_SALE_PKG_QTY)) AS M202407_SALE_PKG_ASP
                         , DECODE(SUM(M202407_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202407_SALE_AMT) / SUM(M202407_SALE_FAB_QTY)) AS M202407_SALE_FAB_ASP
                         , DECODE(SUM(M202407_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202407_SALE_AMT) / SUM(M202407_SALE_EQ_QTY)) AS M202407_SALE_EQ_ASP
                         , SUM(M202407_SALE_AMT)                                    AS M202407_SALE_AMT
                         , SUM(M202407_INV_QTY)                                     AS M202407_INV_QTY
                         , SUM(M202407_INV_PKG_QTY)                                 AS M202407_INV_PKG_QTY
                         , SUM(M202407_INV_FAB_QTY)                                 AS M202407_INV_FAB_QTY
                         , SUM(M202407_INV_EQ_QTY)                                  AS M202407_INV_EQ_QTY
                         , SUM(M202408_SALE_QTY)                                    AS M202408_SALE_QTY
                         , SUM(M202408_SALE_PKG_QTY)                                AS M202408_SALE_PKG_QTY
                         , SUM(M202408_SALE_FAB_QTY)                                AS M202408_SALE_FAB_QTY
                         , SUM(M202408_SALE_EQ_QTY)                                 AS M202408_SALE_EQ_QTY
                         , DECODE(SUM(M202408_SALE_QTY), 0
                                , 0
                                , SUM(M202408_SALE_AMT) / SUM(M202408_SALE_QTY)) AS M202408_SALE_ASP
                         , DECODE(SUM(M202408_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202408_SALE_AMT) / SUM(M202408_SALE_PKG_QTY)) AS M202408_SALE_PKG_ASP
                         , DECODE(SUM(M202408_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202408_SALE_AMT) / SUM(M202408_SALE_FAB_QTY)) AS M202408_SALE_FAB_ASP
                         , DECODE(SUM(M202408_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202408_SALE_AMT) / SUM(M202408_SALE_EQ_QTY)) AS M202408_SALE_EQ_ASP
                         , SUM(M202408_SALE_AMT)                                    AS M202408_SALE_AMT
                         , SUM(M202408_INV_QTY)                                     AS M202408_INV_QTY
                         , SUM(M202408_INV_PKG_QTY)                                 AS M202408_INV_PKG_QTY
                         , SUM(M202408_INV_FAB_QTY)                                 AS M202408_INV_FAB_QTY
                         , SUM(M202408_INV_EQ_QTY)                                  AS M202408_INV_EQ_QTY
                         , SUM(M202409_SALE_QTY)                                    AS M202409_SALE_QTY
                         , SUM(M202409_SALE_PKG_QTY)                                AS M202409_SALE_PKG_QTY
                         , SUM(M202409_SALE_FAB_QTY)                                AS M202409_SALE_FAB_QTY
                         , SUM(M202409_SALE_EQ_QTY)                                 AS M202409_SALE_EQ_QTY
                         , DECODE(SUM(M202409_SALE_QTY), 0
                                , 0
                                , SUM(M202409_SALE_AMT) / SUM(M202409_SALE_QTY)) AS M202409_SALE_ASP
                         , DECODE(SUM(M202409_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202409_SALE_AMT) / SUM(M202409_SALE_PKG_QTY)) AS M202409_SALE_PKG_ASP
                         , DECODE(SUM(M202409_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202409_SALE_AMT) / SUM(M202409_SALE_FAB_QTY)) AS M202409_SALE_FAB_ASP
                         , DECODE(SUM(M202409_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202409_SALE_AMT) / SUM(M202409_SALE_EQ_QTY)) AS M202409_SALE_EQ_ASP
                         , SUM(M202409_SALE_AMT)                                    AS M202409_SALE_AMT
                         , SUM(M202409_INV_QTY)                                     AS M202409_INV_QTY
                         , SUM(M202409_INV_PKG_QTY)                                 AS M202409_INV_PKG_QTY
                         , SUM(M202409_INV_FAB_QTY)                                 AS M202409_INV_FAB_QTY
                         , SUM(M202409_INV_EQ_QTY)                                  AS M202409_INV_EQ_QTY
                         , SUM(Q202403_SALE_QTY)                                    AS Q202403_SALE_QTY
                         , SUM(Q202403_SALE_PKG_QTY)                                AS Q202403_SALE_PKG_QTY
                         , SUM(Q202403_SALE_FAB_QTY)                                AS Q202403_SALE_FAB_QTY
                         , SUM(Q202403_SALE_EQ_QTY)                                 AS Q202403_SALE_EQ_QTY
                         , SUM(Q202403_SALE_AMT)                                    AS Q202403_SALE_AMT
                         , DECODE(SUM(Q202403_SALE_QTY), 0
                                , 0
                                , SUM(Q202403_SALE_AMT) / SUM(Q202403_SALE_QTY)) AS Q202403_SALE_ASP
                         , DECODE(SUM(Q202403_SALE_PKG_QTY), 0
                                , 0
                                , SUM(Q202403_SALE_AMT) / SUM(Q202403_SALE_PKG_QTY)) AS Q202403_SALE_PKG_ASP
                         , DECODE(SUM(Q202403_SALE_FAB_QTY), 0
                                , 0
                                , SUM(Q202403_SALE_AMT) / SUM(Q202403_SALE_FAB_QTY)) AS Q202403_SALE_FAB_ASP
                         , DECODE(SUM(Q202403_SALE_EQ_QTY), 0
                                , 0
                                , SUM(Q202403_SALE_AMT) / SUM(Q202403_SALE_EQ_QTY)) AS Q202403_SALE_EQ_ASP
                         , SUM(Q202403_INV_QTY)                                     AS Q202403_INV_QTY
                         , SUM(Q202403_INV_PKG_QTY)                                 AS Q202403_INV_PKG_QTY
                         , SUM(Q202403_INV_FAB_QTY)                                 AS Q202403_INV_FAB_QTY
                         , SUM(Q202403_INV_EQ_QTY)                                  AS Q202403_INV_EQ_QTY
                         , SUM(M202410_SALE_QTY)                                    AS M202410_SALE_QTY
                         , SUM(M202410_SALE_PKG_QTY)                                AS M202410_SALE_PKG_QTY
                         , SUM(M202410_SALE_FAB_QTY)                                AS M202410_SALE_FAB_QTY
                         , SUM(M202410_SALE_EQ_QTY)                                 AS M202410_SALE_EQ_QTY
                         , DECODE(SUM(M202410_SALE_QTY), 0
                                , 0
                                , SUM(M202410_SALE_AMT) / SUM(M202410_SALE_QTY)) AS M202410_SALE_ASP
                         , DECODE(SUM(M202410_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202410_SALE_AMT) / SUM(M202410_SALE_PKG_QTY)) AS M202410_SALE_PKG_ASP
                         , DECODE(SUM(M202410_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202410_SALE_AMT) / SUM(M202410_SALE_FAB_QTY)) AS M202410_SALE_FAB_ASP
                         , DECODE(SUM(M202410_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202410_SALE_AMT) / SUM(M202410_SALE_EQ_QTY)) AS M202410_SALE_EQ_ASP
                         , SUM(M202410_SALE_AMT)                                    AS M202410_SALE_AMT
                         , SUM(M202410_INV_QTY)                                     AS M202410_INV_QTY
                         , SUM(M202410_INV_PKG_QTY)                                 AS M202410_INV_PKG_QTY
                         , SUM(M202410_INV_FAB_QTY)                                 AS M202410_INV_FAB_QTY
                         , SUM(M202410_INV_EQ_QTY)                                  AS M202410_INV_EQ_QTY
                         , SUM(M202411_SALE_QTY)                                    AS M202411_SALE_QTY
                         , SUM(M202411_SALE_PKG_QTY)                                AS M202411_SALE_PKG_QTY
                         , SUM(M202411_SALE_FAB_QTY)                                AS M202411_SALE_FAB_QTY
                         , SUM(M202411_SALE_EQ_QTY)                                 AS M202411_SALE_EQ_QTY
                         , DECODE(SUM(M202411_SALE_QTY), 0
                                , 0
                                , SUM(M202411_SALE_AMT) / SUM(M202411_SALE_QTY)) AS M202411_SALE_ASP
                         , DECODE(SUM(M202411_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202411_SALE_AMT) / SUM(M202411_SALE_PKG_QTY)) AS M202411_SALE_PKG_ASP
                         , DECODE(SUM(M202411_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202411_SALE_AMT) / SUM(M202411_SALE_FAB_QTY)) AS M202411_SALE_FAB_ASP
                         , DECODE(SUM(M202411_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202411_SALE_AMT) / SUM(M202411_SALE_EQ_QTY)) AS M202411_SALE_EQ_ASP
                         , SUM(M202411_SALE_AMT)                                    AS M202411_SALE_AMT
                         , SUM(M202411_INV_QTY)                                     AS M202411_INV_QTY
                         , SUM(M202411_INV_PKG_QTY)                                 AS M202411_INV_PKG_QTY
                         , SUM(M202411_INV_FAB_QTY)                                 AS M202411_INV_FAB_QTY
                         , SUM(M202411_INV_EQ_QTY)                                  AS M202411_INV_EQ_QTY
                         , SUM(M202412_SALE_QTY)                                    AS M202412_SALE_QTY
                         , SUM(M202412_SALE_PKG_QTY)                                AS M202412_SALE_PKG_QTY
                         , SUM(M202412_SALE_FAB_QTY)                                AS M202412_SALE_FAB_QTY
                         , SUM(M202412_SALE_EQ_QTY)                                 AS M202412_SALE_EQ_QTY
                         , DECODE(SUM(M202412_SALE_QTY), 0
                                , 0
                                , SUM(M202412_SALE_AMT) / SUM(M202412_SALE_QTY)) AS M202412_SALE_ASP
                         , DECODE(SUM(M202412_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202412_SALE_AMT) / SUM(M202412_SALE_PKG_QTY)) AS M202412_SALE_PKG_ASP
                         , DECODE(SUM(M202412_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202412_SALE_AMT) / SUM(M202412_SALE_FAB_QTY)) AS M202412_SALE_FAB_ASP
                         , DECODE(SUM(M202412_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202412_SALE_AMT) / SUM(M202412_SALE_EQ_QTY)) AS M202412_SALE_EQ_ASP
                         , SUM(M202412_SALE_AMT)                                    AS M202412_SALE_AMT
                         , SUM(M202412_INV_QTY)                                     AS M202412_INV_QTY
                         , SUM(M202412_INV_PKG_QTY)                                 AS M202412_INV_PKG_QTY
                         , SUM(M202412_INV_FAB_QTY)                                 AS M202412_INV_FAB_QTY
                         , SUM(M202412_INV_EQ_QTY)                                  AS M202412_INV_EQ_QTY
                         , SUM(Q202404_SALE_QTY)                                    AS Q202404_SALE_QTY
                         , SUM(Q202404_SALE_PKG_QTY)                                AS Q202404_SALE_PKG_QTY
                         , SUM(Q202404_SALE_FAB_QTY)                                AS Q202404_SALE_FAB_QTY
                         , SUM(Q202404_SALE_EQ_QTY)                                 AS Q202404_SALE_EQ_QTY
                         , SUM(Q202404_SALE_AMT)                                    AS Q202404_SALE_AMT
                         , DECODE(SUM(Q202404_SALE_QTY), 0
                                , 0
                                , SUM(Q202404_SALE_AMT) / SUM(Q202404_SALE_QTY)) AS Q202404_SALE_ASP
                         , DECODE(SUM(Q202404_SALE_PKG_QTY), 0
                                , 0
                                , SUM(Q202404_SALE_AMT) / SUM(Q202404_SALE_PKG_QTY)) AS Q202404_SALE_PKG_ASP
                         , DECODE(SUM(Q202404_SALE_FAB_QTY), 0
                                , 0
                                , SUM(Q202404_SALE_AMT) / SUM(Q202404_SALE_FAB_QTY)) AS Q202404_SALE_FAB_ASP
                         , DECODE(SUM(Q202404_SALE_EQ_QTY), 0
                                , 0
                                , SUM(Q202404_SALE_AMT) / SUM(Q202404_SALE_EQ_QTY)) AS Q202404_SALE_EQ_ASP
                         , SUM(Q202404_INV_QTY)                                     AS Q202404_INV_QTY
                         , SUM(Q202404_INV_PKG_QTY)                                 AS Q202404_INV_PKG_QTY
                         , SUM(Q202404_INV_FAB_QTY)                                 AS Q202404_INV_FAB_QTY
                         , SUM(Q202404_INV_EQ_QTY)                                  AS Q202404_INV_EQ_QTY
                         , SUM(H202402_SALE_QTY)                                    AS H202402_SALE_QTY
                         , SUM(H202402_SALE_PKG_QTY)                                AS H202402_SALE_PKG_QTY
                         , SUM(H202402_SALE_FAB_QTY)                                AS H202402_SALE_FAB_QTY
                         , SUM(H202402_SALE_EQ_QTY)                                 AS H202402_SALE_EQ_QTY
                         , SUM(H202402_SALE_AMT)                                    AS H202402_SALE_AMT
                         , DECODE(SUM(H202402_SALE_QTY), 0
                                , 0
                                , SUM(H202402_SALE_AMT) / SUM(H202402_SALE_QTY)) AS H202402_SALE_ASP
                         , DECODE(SUM(H202402_SALE_PKG_QTY), 0
                                , 0
                                , SUM(H202402_SALE_AMT) / SUM(H202402_SALE_PKG_QTY)) AS H202402_SALE_PKG_ASP
                         , DECODE(SUM(H202402_SALE_FAB_QTY), 0
                                , 0
                                , SUM(H202402_SALE_AMT) / SUM(H202402_SALE_FAB_QTY)) AS H202402_SALE_FAB_ASP
                         , DECODE(SUM(H202402_SALE_EQ_QTY), 0
                                , 0
                                , SUM(H202402_SALE_AMT) / SUM(H202402_SALE_EQ_QTY)) AS H202402_SALE_EQ_ASP
                         , SUM(H202402_INV_QTY)                                     AS H202402_INV_QTY
                         , SUM(H202402_INV_PKG_QTY)                                 AS H202402_INV_PKG_QTY
                         , SUM(H202402_INV_FAB_QTY)                                 AS H202402_INV_FAB_QTY
                         , SUM(H202402_INV_EQ_QTY)                                  AS H202402_INV_EQ_QTY
                         , SUM(Y2024_SALE_QTY)                                      AS Y2024_SALE_QTY
                         , SUM(Y2024_SALE_PKG_QTY)                                  AS Y2024_SALE_PKG_QTY
                         , SUM(Y2024_SALE_FAB_QTY)                                  AS Y2024_SALE_FAB_QTY
                         , SUM(Y2024_SALE_EQ_QTY)                                   AS Y2024_SALE_EQ_QTY
                         , SUM(Y2024_SALE_AMT)                                      AS Y2024_SALE_AMT
                         , DECODE(SUM(Y2024_SALE_QTY), 0
                                , 0
                                , SUM(Y2024_SALE_AMT) / SUM(Y2024_SALE_QTY)) AS Y2024_SALE_ASP
                         , DECODE(SUM(Y2024_SALE_PKG_QTY), 0
                                , 0
                                , SUM(Y2024_SALE_AMT) / SUM(Y2024_SALE_PKG_QTY)) AS Y2024_SALE_PKG_ASP
                         , DECODE(SUM(Y2024_SALE_FAB_QTY), 0
                                , 0
                                , SUM(Y2024_SALE_AMT) / SUM(Y2024_SALE_FAB_QTY)) AS Y2024_SALE_FAB_ASP
                         , DECODE(SUM(Y2024_SALE_EQ_QTY), 0
                                , 0
                                , SUM(Y2024_SALE_AMT) / SUM(Y2024_SALE_EQ_QTY)) AS Y2024_SALE_EQ_ASP
                         , SUM(Y2024_INV_QTY)                                   AS Y2024_INV_QTY
                         , SUM(Y2024_INV_PKG_QTY)                               AS Y2024_INV_PKG_QTY
                         , SUM(Y2024_INV_FAB_QTY)                               AS Y2024_INV_FAB_QTY
                         , SUM(Y2024_INV_EQ_QTY)                                AS Y2024_INV_EQ_QTY
                         , SUM(M202501_SALE_QTY)                                AS M202501_SALE_QTY
                         , SUM(M202501_SALE_PKG_QTY)                            AS M202501_SALE_PKG_QTY
                         , SUM(M202501_SALE_FAB_QTY)                            AS M202501_SALE_FAB_QTY
                         , SUM(M202501_SALE_EQ_QTY)                             AS M202501_SALE_EQ_QTY
                         , DECODE(SUM(M202501_SALE_QTY), 0
                                , 0
                                , SUM(M202501_SALE_AMT) / SUM(M202501_SALE_QTY)) AS M202501_SALE_ASP
                         , DECODE(SUM(M202501_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202501_SALE_AMT) / SUM(M202501_SALE_PKG_QTY)) AS M202501_SALE_PKG_ASP
                         , DECODE(SUM(M202501_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202501_SALE_AMT) / SUM(M202501_SALE_FAB_QTY)) AS M202501_SALE_FAB_ASP
                         , DECODE(SUM(M202501_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202501_SALE_AMT) / SUM(M202501_SALE_EQ_QTY)) AS M202501_SALE_EQ_ASP
                         , SUM(M202501_SALE_AMT)                                    AS M202501_SALE_AMT
                         , SUM(M202501_INV_QTY)                                     AS M202501_INV_QTY
                         , SUM(M202501_INV_PKG_QTY)                                 AS M202501_INV_PKG_QTY
                         , SUM(M202501_INV_FAB_QTY)                                 AS M202501_INV_FAB_QTY
                         , SUM(M202501_INV_EQ_QTY)                                  AS M202501_INV_EQ_QTY
                         , SUM(M202502_SALE_QTY)                                    AS M202502_SALE_QTY
                         , SUM(M202502_SALE_PKG_QTY)                                AS M202502_SALE_PKG_QTY
                         , SUM(M202502_SALE_FAB_QTY)                                AS M202502_SALE_FAB_QTY
                         , SUM(M202502_SALE_EQ_QTY)                                 AS M202502_SALE_EQ_QTY
                         , DECODE(SUM(M202502_SALE_QTY), 0
                                , 0
                                , SUM(M202502_SALE_AMT) / SUM(M202502_SALE_QTY)) AS M202502_SALE_ASP
                         , DECODE(SUM(M202502_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202502_SALE_AMT) / SUM(M202502_SALE_PKG_QTY)) AS M202502_SALE_PKG_ASP
                         , DECODE(SUM(M202502_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202502_SALE_AMT) / SUM(M202502_SALE_FAB_QTY)) AS M202502_SALE_FAB_ASP
                         , DECODE(SUM(M202502_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202502_SALE_AMT) / SUM(M202502_SALE_EQ_QTY)) AS M202502_SALE_EQ_ASP
                         , SUM(M202502_SALE_AMT)                                    AS M202502_SALE_AMT
                         , SUM(M202502_INV_QTY)                                     AS M202502_INV_QTY
                         , SUM(M202502_INV_PKG_QTY)                                 AS M202502_INV_PKG_QTY
                         , SUM(M202502_INV_FAB_QTY)                                 AS M202502_INV_FAB_QTY
                         , SUM(M202502_INV_EQ_QTY)                                  AS M202502_INV_EQ_QTY
                         , SUM(M202503_SALE_QTY)                                    AS M202503_SALE_QTY
                         , SUM(M202503_SALE_PKG_QTY)                                AS M202503_SALE_PKG_QTY
                         , SUM(M202503_SALE_FAB_QTY)                                AS M202503_SALE_FAB_QTY
                         , SUM(M202503_SALE_EQ_QTY)                                 AS M202503_SALE_EQ_QTY
                         , DECODE(SUM(M202503_SALE_QTY), 0
                                , 0
                                , SUM(M202503_SALE_AMT) / SUM(M202503_SALE_QTY)) AS M202503_SALE_ASP
                         , DECODE(SUM(M202503_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202503_SALE_AMT) / SUM(M202503_SALE_PKG_QTY)) AS M202503_SALE_PKG_ASP
                         , DECODE(SUM(M202503_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202503_SALE_AMT) / SUM(M202503_SALE_FAB_QTY)) AS M202503_SALE_FAB_ASP
                         , DECODE(SUM(M202503_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202503_SALE_AMT) / SUM(M202503_SALE_EQ_QTY)) AS M202503_SALE_EQ_ASP
                         , SUM(M202503_SALE_AMT)                                    AS M202503_SALE_AMT
                         , SUM(M202503_INV_QTY)                                     AS M202503_INV_QTY
                         , SUM(M202503_INV_PKG_QTY)                                 AS M202503_INV_PKG_QTY
                         , SUM(M202503_INV_FAB_QTY)                                 AS M202503_INV_FAB_QTY
                         , SUM(M202503_INV_EQ_QTY)                                  AS M202503_INV_EQ_QTY
                         , SUM(Q202501_SALE_QTY)                                    AS Q202501_SALE_QTY
                         , SUM(Q202501_SALE_PKG_QTY)                                AS Q202501_SALE_PKG_QTY
                         , SUM(Q202501_SALE_FAB_QTY)                                AS Q202501_SALE_FAB_QTY
                         , SUM(Q202501_SALE_EQ_QTY)                                 AS Q202501_SALE_EQ_QTY
                         , SUM(Q202501_SALE_AMT)                                    AS Q202501_SALE_AMT
                         , DECODE(SUM(Q202501_SALE_QTY), 0
                                , 0
                                , SUM(Q202501_SALE_AMT) / SUM(Q202501_SALE_QTY)) AS Q202501_SALE_ASP
                         , DECODE(SUM(Q202501_SALE_PKG_QTY), 0
                                , 0
                                , SUM(Q202501_SALE_AMT) / SUM(Q202501_SALE_PKG_QTY)) AS Q202501_SALE_PKG_ASP
                         , DECODE(SUM(Q202501_SALE_FAB_QTY), 0
                                , 0
                                , SUM(Q202501_SALE_AMT) / SUM(Q202501_SALE_FAB_QTY)) AS Q202501_SALE_FAB_ASP
                         , DECODE(SUM(Q202501_SALE_EQ_QTY), 0
                                , 0
                                , SUM(Q202501_SALE_AMT) / SUM(Q202501_SALE_EQ_QTY)) AS Q202501_SALE_EQ_ASP
                         , SUM(Q202501_INV_QTY)                                     AS Q202501_INV_QTY
                         , SUM(Q202501_INV_PKG_QTY)                                 AS Q202501_INV_PKG_QTY
                         , SUM(Q202501_INV_FAB_QTY)                                 AS Q202501_INV_FAB_QTY
                         , SUM(Q202501_INV_EQ_QTY)                                  AS Q202501_INV_EQ_QTY
                         , SUM(M202504_SALE_QTY)                                    AS M202504_SALE_QTY
                         , SUM(M202504_SALE_PKG_QTY)                                AS M202504_SALE_PKG_QTY
                         , SUM(M202504_SALE_FAB_QTY)                                AS M202504_SALE_FAB_QTY
                         , SUM(M202504_SALE_EQ_QTY)                                 AS M202504_SALE_EQ_QTY
                         , DECODE(SUM(M202504_SALE_QTY), 0
                                , 0
                                , SUM(M202504_SALE_AMT) / SUM(M202504_SALE_QTY)) AS M202504_SALE_ASP
                         , DECODE(SUM(M202504_SALE_PKG_QTY), 0
                                , 0
                                , SUM(M202504_SALE_AMT) / SUM(M202504_SALE_PKG_QTY)) AS M202504_SALE_PKG_ASP
                         , DECODE(SUM(M202504_SALE_FAB_QTY), 0
                                , 0
                                , SUM(M202504_SALE_AMT) / SUM(M202504_SALE_FAB_QTY)) AS M202504_SALE_FAB_ASP
                         , DECODE(SUM(M202504_SALE_EQ_QTY), 0
                                , 0
                                , SUM(M202504_SALE_AMT) / SUM(M202504_SALE_EQ_QTY)) AS M202504_SALE_EQ_ASP
                         , SUM(M202504_SALE_AMT)                                    AS M202504_SALE_AMT
                         , SUM(M202504_INV_QTY)                                     AS M202504_INV_QTY
                         , SUM(M202504_INV_PKG_QTY)                                 AS M202504_INV_PKG_QTY
                         , SUM(M202504_INV_FAB_QTY)                                 AS M202504_INV_FAB_QTY
                         , SUM(M202504_INV_EQ_QTY)                                  AS M202504_INV_EQ_QTY
                         , SUM(Q202502_SALE_QTY)                                    AS Q202502_SALE_QTY
                         , SUM(Q202502_SALE_PKG_QTY)                                AS Q202502_SALE_PKG_QTY
                         , SUM(Q202502_SALE_FAB_QTY)                                AS Q202502_SALE_FAB_QTY
                         , SUM(Q202502_SALE_EQ_QTY)                                 AS Q202502_SALE_EQ_QTY
                         , SUM(Q202502_SALE_AMT)                                    AS Q202502_SALE_AMT
                         , DECODE(SUM(Q202502_SALE_QTY), 0
                                , 0
                                , SUM(Q202502_SALE_AMT) / SUM(Q202502_SALE_QTY)) AS Q202502_SALE_ASP
                         , DECODE(SUM(Q202502_SALE_PKG_QTY), 0
                                , 0
                                , SUM(Q202502_SALE_AMT) / SUM(Q202502_SALE_PKG_QTY)) AS Q202502_SALE_PKG_ASP
                         , DECODE(SUM(Q202502_SALE_FAB_QTY), 0
                                , 0
                                , SUM(Q202502_SALE_AMT) / SUM(Q202502_SALE_FAB_QTY)) AS Q202502_SALE_FAB_ASP
                         , DECODE(SUM(Q202502_SALE_EQ_QTY), 0
                                , 0
                                , SUM(Q202502_SALE_AMT) / SUM(Q202502_SALE_EQ_QTY)) AS Q202502_SALE_EQ_ASP
                         , SUM(Q202502_INV_QTY)                                     AS Q202502_INV_QTY
                         , SUM(Q202502_INV_PKG_QTY)                                 AS Q202502_INV_PKG_QTY
                         , SUM(Q202502_INV_FAB_QTY)                                 AS Q202502_INV_FAB_QTY
                         , SUM(Q202502_INV_EQ_QTY)                                  AS Q202502_INV_EQ_QTY
                         , SUM(H202501_SALE_QTY)                                    AS H202501_SALE_QTY
                         , SUM(H202501_SALE_PKG_QTY)                                AS H202501_SALE_PKG_QTY
                         , SUM(H202501_SALE_FAB_QTY)                                AS H202501_SALE_FAB_QTY
                         , SUM(H202501_SALE_EQ_QTY)                                 AS H202501_SALE_EQ_QTY
                         , SUM(H202501_SALE_AMT)                                    AS H202501_SALE_AMT
                         , DECODE(SUM(H202501_SALE_QTY), 0
                                , 0
                                , SUM(H202501_SALE_AMT) / SUM(H202501_SALE_QTY)) AS H202501_SALE_ASP
                         , DECODE(SUM(H202501_SALE_PKG_QTY), 0
                                , 0
                                , SUM(H202501_SALE_AMT) / SUM(H202501_SALE_PKG_QTY)) AS H202501_SALE_PKG_ASP
                         , DECODE(SUM(H202501_SALE_FAB_QTY), 0
                                , 0
                                , SUM(H202501_SALE_AMT) / SUM(H202501_SALE_FAB_QTY)) AS H202501_SALE_FAB_ASP
                         , DECODE(SUM(H202501_SALE_EQ_QTY), 0
                                , 0
                                , SUM(H202501_SALE_AMT) / SUM(H202501_SALE_EQ_QTY)) AS H202501_SALE_EQ_ASP
                         , SUM(H202501_INV_QTY)                                     AS H202501_INV_QTY
                         , SUM(H202501_INV_PKG_QTY)                                 AS H202501_INV_PKG_QTY
                         , SUM(H202501_INV_FAB_QTY)                                 AS H202501_INV_FAB_QTY
                         , SUM(H202501_INV_EQ_QTY)                                  AS H202501_INV_EQ_QTY
                         , SUM(Y2025_SALE_QTY)                                      AS Y2025_SALE_QTY
                         , SUM(Y2025_SALE_PKG_QTY)                                  AS Y2025_SALE_PKG_QTY
                         , SUM(Y2025_SALE_FAB_QTY)                                  AS Y2025_SALE_FAB_QTY
                         , SUM(Y2025_SALE_EQ_QTY)                                   AS Y2025_SALE_EQ_QTY
                         , SUM(Y2025_SALE_AMT)                                      AS Y2025_SALE_AMT
                         , DECODE(SUM(Y2025_SALE_QTY), 0
                                , 0
                                , SUM(Y2025_SALE_AMT) / SUM(Y2025_SALE_QTY)) AS Y2025_SALE_ASP
                         , DECODE(SUM(Y2025_SALE_PKG_QTY), 0
                                , 0
                                , SUM(Y2025_SALE_AMT) / SUM(Y2025_SALE_PKG_QTY)) AS Y2025_SALE_PKG_ASP
                         , DECODE(SUM(Y2025_SALE_FAB_QTY), 0
                                , 0
                                , SUM(Y2025_SALE_AMT) / SUM(Y2025_SALE_FAB_QTY)) AS Y2025_SALE_FAB_ASP
                         , DECODE(SUM(Y2025_SALE_EQ_QTY), 0
                                , 0
                                , SUM(Y2025_SALE_AMT) / SUM(Y2025_SALE_EQ_QTY)) AS Y2025_SALE_EQ_ASP
                         , SUM(Y2025_INV_QTY)                                   AS Y2025_INV_QTY
                         , SUM(Y2025_INV_PKG_QTY)                               AS Y2025_INV_PKG_QTY
                         , SUM(Y2025_INV_FAB_QTY)                               AS Y2025_INV_FAB_QTY
                         , SUM(Y2025_INV_EQ_QTY)                                AS Y2025_INV_EQ_QTY
                         , SUM(TOTAL_SALE_QTY)                                  AS TOTAL_SALE_QTY
                         , SUM(TOTAL_SALE_PKG_QTY)                              AS TOTAL_SALE_PKG_QTY
                         , SUM(TOTAL_SALE_FAB_QTY)                              AS TOTAL_SALE_FAB_QTY
                         , SUM(TOTAL_SALE_EQ_QTY)                               AS TOTAL_SALE_EQ_QTY
                         , SUM(TOTAL_SALE_AMT)                                  AS TOTAL_SALE_AMT
                         , DECODE(SUM(TOTAL_SALE_QTY), 0
                                , 0
                                , SUM(TOTAL_SALE_AMT) / SUM(TOTAL_SALE_QTY)) AS TOTAL_SALE_ASP
                         , DECODE(SUM(TOTAL_SALE_PKG_QTY), 0
                                , 0
                                , SUM(TOTAL_SALE_AMT) / SUM(TOTAL_SALE_PKG_QTY)) AS TOTAL_SALE_PKG_ASP
                         , DECODE(SUM(TOTAL_SALE_FAB_QTY), 0
                                , 0
                                , SUM(TOTAL_SALE_AMT) / SUM(TOTAL_SALE_FAB_QTY)) AS TOTAL_SALE_FAB_ASP
                         , DECODE(SUM(TOTAL_SALE_EQ_QTY), 0
                                , 0
                                , SUM(TOTAL_SALE_AMT) / SUM(TOTAL_SALE_EQ_QTY)) AS TOTAL_SALE_EQ_ASP
                         , SUM(TOTAL_INV_QTY)                                   AS TOTAL_INV_QTY
                         , SUM(TOTAL_INV_PKG_QTY)                               AS TOTAL_INV_PKG_QTY
                         , SUM(TOTAL_INV_FAB_QTY)                               AS TOTAL_INV_FAB_QTY
                         , SUM(TOTAL_INV_EQ_QTY)                                AS TOTAL_INV_EQ_QTY
                         , CASE
                                    WHEN NVL(SUM(M202401_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202402_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202403_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202404_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202405_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202406_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202407_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202408_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202409_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202410_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202411_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202412_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202501_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202502_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202503_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202504_SALE_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END AS TOTAL_SALE_QTY_CNT
                         , CASE
                                    WHEN NVL(DECODE(SUM(M202401_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202401_SALE_AMT) / SUM(M202401_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(DECODE(SUM(M202402_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202402_SALE_AMT) / SUM(M202402_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(DECODE(SUM(M202403_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202403_SALE_AMT) / SUM(M202403_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(DECODE(SUM(M202404_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202404_SALE_AMT) / SUM(M202404_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(DECODE(SUM(M202405_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202405_SALE_AMT) / SUM(M202405_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(DECODE(SUM(M202406_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202406_SALE_AMT) / SUM(M202406_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(DECODE(SUM(M202407_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202407_SALE_AMT) / SUM(M202407_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(DECODE(SUM(M202408_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202408_SALE_AMT) / SUM(M202408_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(DECODE(SUM(M202409_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202409_SALE_AMT) / SUM(M202409_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(DECODE(SUM(M202410_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202410_SALE_AMT) / SUM(M202410_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(DECODE(SUM(M202411_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202411_SALE_AMT) / SUM(M202411_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(DECODE(SUM(M202412_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202412_SALE_AMT) / SUM(M202412_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(DECODE(SUM(M202501_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202501_SALE_AMT) / SUM(M202501_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(DECODE(SUM(M202502_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202502_SALE_AMT) / SUM(M202502_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(DECODE(SUM(M202503_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202503_SALE_AMT) / SUM(M202503_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(DECODE(SUM(M202504_SALE_QTY), 0
                                                  , 0
                                                  , SUM(M202504_SALE_AMT) / SUM(M202504_SALE_QTY)), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END AS TOTAL_SALE_ASP_CNT
                         , CASE
                                    WHEN NVL(SUM(M202401_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202402_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202403_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202404_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202405_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202406_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202407_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202408_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202409_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202410_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202411_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202412_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202501_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202502_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202503_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202504_SALE_AMT), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END AS TOTAL_SALE_AMT_CNT
                         , CASE
                                    WHEN NVL(SUM(M202401_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202402_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202403_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202404_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202405_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202406_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202407_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202408_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202409_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202410_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202411_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202412_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202501_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202502_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202503_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END +
                           CASE
                                    WHEN NVL(SUM(M202504_INV_QTY), 0) <> 0
                                    THEN 1
                                    ELSE 0
                           END AS TOTAL_INV_QTY_CNT
                      FROM(
                                  SELECT SCM_FAMILY_CD
                                       , TECH_CD
                                       , FAB_DEN_CD
                                       , CHG_PROD_MODE_CD
                                       , CELL_LAYER_TYP_CD
                                       , PLN_REV
                                         /* ASP 데이터생성 */
                                       , M202401_SALE_QTY
                                       , M202401_SALE_PKG_QTY
                                       , M202401_SALE_FAB_QTY
                                       , M202401_SALE_EQ_QTY
                                       , M202401_SALE_ASP
                                       , M202401_SALE_PKG_ASP
                                       , M202401_SALE_FAB_ASP
                                       , M202401_SALE_EQ_ASP
                                       , M202401_SALE_AMT
                                       , M202401_INV_QTY
                                       , M202401_INV_PKG_QTY
                                       , M202401_INV_FAB_QTY
                                       , M202401_INV_EQ_QTY
                                       , M202402_SALE_QTY
                                       , M202402_SALE_PKG_QTY
                                       , M202402_SALE_FAB_QTY
                                       , M202402_SALE_EQ_QTY
                                       , M202402_SALE_ASP
                                       , M202402_SALE_PKG_ASP
                                       , M202402_SALE_FAB_ASP
                                       , M202402_SALE_EQ_ASP
                                       , M202402_SALE_AMT
                                       , M202402_INV_QTY
                                       , M202402_INV_PKG_QTY
                                       , M202402_INV_FAB_QTY
                                       , M202402_INV_EQ_QTY
                                       , M202403_SALE_QTY
                                       , M202403_SALE_PKG_QTY
                                       , M202403_SALE_FAB_QTY
                                       , M202403_SALE_EQ_QTY
                                       , M202403_SALE_ASP
                                       , M202403_SALE_PKG_ASP
                                       , M202403_SALE_FAB_ASP
                                       , M202403_SALE_EQ_ASP
                                       , M202403_SALE_AMT
                                       , M202403_INV_QTY
                                       , M202403_INV_PKG_QTY
                                       , M202403_INV_FAB_QTY
                                       , M202403_INV_EQ_QTY
                                       , Q202401_SALE_QTY
                                       , Q202401_SALE_PKG_QTY
                                       , Q202401_SALE_FAB_QTY
                                       , Q202401_SALE_EQ_QTY
                                       , Q202401_SALE_AMT
                                       , Q202401_INV_QTY
                                       , Q202401_INV_PKG_QTY
                                       , Q202401_INV_FAB_QTY
                                       , Q202401_INV_EQ_QTY
                                       , M202404_SALE_QTY
                                       , M202404_SALE_PKG_QTY
                                       , M202404_SALE_FAB_QTY
                                       , M202404_SALE_EQ_QTY
                                       , M202404_SALE_ASP
                                       , M202404_SALE_PKG_ASP
                                       , M202404_SALE_FAB_ASP
                                       , M202404_SALE_EQ_ASP
                                       , M202404_SALE_AMT
                                       , M202404_INV_QTY
                                       , M202404_INV_PKG_QTY
                                       , M202404_INV_FAB_QTY
                                       , M202404_INV_EQ_QTY
                                       , M202405_SALE_QTY
                                       , M202405_SALE_PKG_QTY
                                       , M202405_SALE_FAB_QTY
                                       , M202405_SALE_EQ_QTY
                                       , M202405_SALE_ASP
                                       , M202405_SALE_PKG_ASP
                                       , M202405_SALE_FAB_ASP
                                       , M202405_SALE_EQ_ASP
                                       , M202405_SALE_AMT
                                       , M202405_INV_QTY
                                       , M202405_INV_PKG_QTY
                                       , M202405_INV_FAB_QTY
                                       , M202405_INV_EQ_QTY
                                       , M202406_SALE_QTY
                                       , M202406_SALE_PKG_QTY
                                       , M202406_SALE_FAB_QTY
                                       , M202406_SALE_EQ_QTY
                                       , M202406_SALE_ASP
                                       , M202406_SALE_PKG_ASP
                                       , M202406_SALE_FAB_ASP
                                       , M202406_SALE_EQ_ASP
                                       , M202406_SALE_AMT
                                       , M202406_INV_QTY
                                       , M202406_INV_PKG_QTY
                                       , M202406_INV_FAB_QTY
                                       , M202406_INV_EQ_QTY
                                       , Q202402_SALE_QTY
                                       , Q202402_SALE_PKG_QTY
                                       , Q202402_SALE_FAB_QTY
                                       , Q202402_SALE_EQ_QTY
                                       , Q202402_SALE_AMT
                                       , Q202402_INV_QTY
                                       , Q202402_INV_PKG_QTY
                                       , Q202402_INV_FAB_QTY
                                       , Q202402_INV_EQ_QTY
                                       , H202401_SALE_QTY
                                       , H202401_SALE_PKG_QTY
                                       , H202401_SALE_FAB_QTY
                                       , H202401_SALE_EQ_QTY
                                       , H202401_SALE_AMT
                                       , DECODE(H202401_SALE_QTY, 0
                                              , 0
                                              , H202401_SALE_AMT / H202401_SALE_QTY) AS H202401_SALE_ASP
                                       , DECODE(H202401_SALE_PKG_QTY, 0
                                              , 0
                                              , H202401_SALE_AMT / H202401_SALE_PKG_QTY) AS H202401_SALE_PKG_ASP
                                       , DECODE(H202401_SALE_FAB_QTY, 0
                                              , 0
                                              , H202401_SALE_AMT / H202401_SALE_FAB_QTY) AS H202401_SALE_FAB_ASP
                                       , DECODE(H202401_SALE_EQ_QTY, 0
                                              , 0
                                              , H202401_SALE_AMT / H202401_SALE_EQ_QTY) AS H202401_SALE_EQ_ASP
                                       , H202401_INV_QTY
                                       , H202401_INV_PKG_QTY
                                       , H202401_INV_FAB_QTY
                                       , H202401_INV_EQ_QTY
                                       , M202407_SALE_QTY
                                       , M202407_SALE_PKG_QTY
                                       , M202407_SALE_FAB_QTY
                                       , M202407_SALE_EQ_QTY
                                       , M202407_SALE_ASP
                                       , M202407_SALE_PKG_ASP
                                       , M202407_SALE_FAB_ASP
                                       , M202407_SALE_EQ_ASP
                                       , M202407_SALE_AMT
                                       , M202407_INV_QTY
                                       , M202407_INV_PKG_QTY
                                       , M202407_INV_FAB_QTY
                                       , M202407_INV_EQ_QTY
                                       , M202408_SALE_QTY
                                       , M202408_SALE_PKG_QTY
                                       , M202408_SALE_FAB_QTY
                                       , M202408_SALE_EQ_QTY
                                       , M202408_SALE_ASP
                                       , M202408_SALE_PKG_ASP
                                       , M202408_SALE_FAB_ASP
                                       , M202408_SALE_EQ_ASP
                                       , M202408_SALE_AMT
                                       , M202408_INV_QTY
                                       , M202408_INV_PKG_QTY
                                       , M202408_INV_FAB_QTY
                                       , M202408_INV_EQ_QTY
                                       , M202409_SALE_QTY
                                       , M202409_SALE_PKG_QTY
                                       , M202409_SALE_FAB_QTY
                                       , M202409_SALE_EQ_QTY
                                       , M202409_SALE_ASP
                                       , M202409_SALE_PKG_ASP
                                       , M202409_SALE_FAB_ASP
                                       , M202409_SALE_EQ_ASP
                                       , M202409_SALE_AMT
                                       , M202409_INV_QTY
                                       , M202409_INV_PKG_QTY
                                       , M202409_INV_FAB_QTY
                                       , M202409_INV_EQ_QTY
                                       , Q202403_SALE_QTY
                                       , Q202403_SALE_PKG_QTY
                                       , Q202403_SALE_FAB_QTY
                                       , Q202403_SALE_EQ_QTY
                                       , Q202403_SALE_AMT
                                       , Q202403_INV_QTY
                                       , Q202403_INV_PKG_QTY
                                       , Q202403_INV_FAB_QTY
                                       , Q202403_INV_EQ_QTY
                                       , M202410_SALE_QTY
                                       , M202410_SALE_PKG_QTY
                                       , M202410_SALE_FAB_QTY
                                       , M202410_SALE_EQ_QTY
                                       , M202410_SALE_ASP
                                       , M202410_SALE_PKG_ASP
                                       , M202410_SALE_FAB_ASP
                                       , M202410_SALE_EQ_ASP
                                       , M202410_SALE_AMT
                                       , M202410_INV_QTY
                                       , M202410_INV_PKG_QTY
                                       , M202410_INV_FAB_QTY
                                       , M202410_INV_EQ_QTY
                                       , M202411_SALE_QTY
                                       , M202411_SALE_PKG_QTY
                                       , M202411_SALE_FAB_QTY
                                       , M202411_SALE_EQ_QTY
                                       , M202411_SALE_ASP
                                       , M202411_SALE_PKG_ASP
                                       , M202411_SALE_FAB_ASP
                                       , M202411_SALE_EQ_ASP
                                       , M202411_SALE_AMT
                                       , M202411_INV_QTY
                                       , M202411_INV_PKG_QTY
                                       , M202411_INV_FAB_QTY
                                       , M202411_INV_EQ_QTY
                                       , M202412_SALE_QTY
                                       , M202412_SALE_PKG_QTY
                                       , M202412_SALE_FAB_QTY
                                       , M202412_SALE_EQ_QTY
                                       , M202412_SALE_ASP
                                       , M202412_SALE_PKG_ASP
                                       , M202412_SALE_FAB_ASP
                                       , M202412_SALE_EQ_ASP
                                       , M202412_SALE_AMT
                                       , M202412_INV_QTY
                                       , M202412_INV_PKG_QTY
                                       , M202412_INV_FAB_QTY
                                       , M202412_INV_EQ_QTY
                                       , Q202404_SALE_QTY
                                       , Q202404_SALE_PKG_QTY
                                       , Q202404_SALE_FAB_QTY
                                       , Q202404_SALE_EQ_QTY
                                       , Q202404_SALE_AMT
                                       , Q202404_INV_QTY
                                       , Q202404_INV_PKG_QTY
                                       , Q202404_INV_FAB_QTY
                                       , Q202404_INV_EQ_QTY
                                       , H202402_SALE_QTY
                                       , H202402_SALE_PKG_QTY
                                       , H202402_SALE_FAB_QTY
                                       , H202402_SALE_EQ_QTY
                                       , H202402_SALE_AMT
                                       , DECODE(H202402_SALE_QTY, 0
                                              , 0
                                              , H202402_SALE_AMT / H202402_SALE_QTY) AS H202402_SALE_ASP
                                       , DECODE(H202402_SALE_PKG_QTY, 0
                                              , 0
                                              , H202402_SALE_AMT / H202402_SALE_PKG_QTY) AS H202402_SALE_PKG_ASP
                                       , DECODE(H202402_SALE_FAB_QTY, 0
                                              , 0
                                              , H202402_SALE_AMT / H202402_SALE_FAB_QTY) AS H202402_SALE_FAB_ASP
                                       , DECODE(H202402_SALE_EQ_QTY, 0
                                              , 0
                                              , H202402_SALE_AMT / H202402_SALE_EQ_QTY) AS H202402_SALE_EQ_ASP
                                       , H202402_INV_QTY
                                       , H202402_INV_PKG_QTY
                                       , H202402_INV_FAB_QTY
                                       , H202402_INV_EQ_QTY
                                       , Y2024_SALE_QTY
                                       , Y2024_SALE_PKG_QTY
                                       , Y2024_SALE_FAB_QTY
                                       , Y2024_SALE_EQ_QTY
                                       , Y2024_SALE_AMT
                                       , DECODE(Y2024_SALE_QTY, 0
                                              , 0
                                              , Y2024_SALE_AMT / Y2024_SALE_QTY) AS Y2024_SALE_ASP
                                       , DECODE(Y2024_SALE_PKG_QTY, 0
                                              , 0
                                              , Y2024_SALE_AMT / Y2024_SALE_PKG_QTY) AS Y2024_SALE_PKG_ASP
                                       , DECODE(Y2024_SALE_FAB_QTY, 0
                                              , 0
                                              , Y2024_SALE_AMT / Y2024_SALE_FAB_QTY) AS Y2024_SALE_FAB_ASP
                                       , DECODE(Y2024_SALE_EQ_QTY, 0
                                              , 0
                                              , Y2024_SALE_AMT / Y2024_SALE_EQ_QTY) AS Y2024_SALE_EQ_ASP
                                       , Y2024_INV_QTY
                                       , Y2024_INV_PKG_QTY
                                       , Y2024_INV_FAB_QTY
                                       , Y2024_INV_EQ_QTY
                                       , M202501_SALE_QTY
                                       , M202501_SALE_PKG_QTY
                                       , M202501_SALE_FAB_QTY
                                       , M202501_SALE_EQ_QTY
                                       , M202501_SALE_ASP
                                       , M202501_SALE_PKG_ASP
                                       , M202501_SALE_FAB_ASP
                                       , M202501_SALE_EQ_ASP
                                       , M202501_SALE_AMT
                                       , M202501_INV_QTY
                                       , M202501_INV_PKG_QTY
                                       , M202501_INV_FAB_QTY
                                       , M202501_INV_EQ_QTY
                                       , M202502_SALE_QTY
                                       , M202502_SALE_PKG_QTY
                                       , M202502_SALE_FAB_QTY
                                       , M202502_SALE_EQ_QTY
                                       , M202502_SALE_ASP
                                       , M202502_SALE_PKG_ASP
                                       , M202502_SALE_FAB_ASP
                                       , M202502_SALE_EQ_ASP
                                       , M202502_SALE_AMT
                                       , M202502_INV_QTY
                                       , M202502_INV_PKG_QTY
                                       , M202502_INV_FAB_QTY
                                       , M202502_INV_EQ_QTY
                                       , M202503_SALE_QTY
                                       , M202503_SALE_PKG_QTY
                                       , M202503_SALE_FAB_QTY
                                       , M202503_SALE_EQ_QTY
                                       , M202503_SALE_ASP
                                       , M202503_SALE_PKG_ASP
                                       , M202503_SALE_FAB_ASP
                                       , M202503_SALE_EQ_ASP
                                       , M202503_SALE_AMT
                                       , M202503_INV_QTY
                                       , M202503_INV_PKG_QTY
                                       , M202503_INV_FAB_QTY
                                       , M202503_INV_EQ_QTY
                                       , Q202501_SALE_QTY
                                       , Q202501_SALE_PKG_QTY
                                       , Q202501_SALE_FAB_QTY
                                       , Q202501_SALE_EQ_QTY
                                       , Q202501_SALE_AMT
                                       , Q202501_INV_QTY
                                       , Q202501_INV_PKG_QTY
                                       , Q202501_INV_FAB_QTY
                                       , Q202501_INV_EQ_QTY
                                       , M202504_SALE_QTY
                                       , M202504_SALE_PKG_QTY
                                       , M202504_SALE_FAB_QTY
                                       , M202504_SALE_EQ_QTY
                                       , M202504_SALE_ASP
                                       , M202504_SALE_PKG_ASP
                                       , M202504_SALE_FAB_ASP
                                       , M202504_SALE_EQ_ASP
                                       , M202504_SALE_AMT
                                       , M202504_INV_QTY
                                       , M202504_INV_PKG_QTY
                                       , M202504_INV_FAB_QTY
                                       , M202504_INV_EQ_QTY
                                       , Q202502_SALE_QTY
                                       , Q202502_SALE_PKG_QTY
                                       , Q202502_SALE_FAB_QTY
                                       , Q202502_SALE_EQ_QTY
                                       , Q202502_SALE_AMT
                                       , Q202502_INV_QTY
                                       , Q202502_INV_PKG_QTY
                                       , Q202502_INV_FAB_QTY
                                       , Q202502_INV_EQ_QTY
                                       , H202501_SALE_QTY
                                       , H202501_SALE_PKG_QTY
                                       , H202501_SALE_FAB_QTY
                                       , H202501_SALE_EQ_QTY
                                       , H202501_SALE_AMT
                                       , DECODE(H202501_SALE_QTY, 0
                                              , 0
                                              , H202501_SALE_AMT / H202501_SALE_QTY) AS H202501_SALE_ASP
                                       , DECODE(H202501_SALE_PKG_QTY, 0
                                              , 0
                                              , H202501_SALE_AMT / H202501_SALE_PKG_QTY) AS H202501_SALE_PKG_ASP
                                       , DECODE(H202501_SALE_FAB_QTY, 0
                                              , 0
                                              , H202501_SALE_AMT / H202501_SALE_FAB_QTY) AS H202501_SALE_FAB_ASP
                                       , DECODE(H202501_SALE_EQ_QTY, 0
                                              , 0
                                              , H202501_SALE_AMT / H202501_SALE_EQ_QTY) AS H202501_SALE_EQ_ASP
                                       , H202501_INV_QTY
                                       , H202501_INV_PKG_QTY
                                       , H202501_INV_FAB_QTY
                                       , H202501_INV_EQ_QTY
                                       , Y2025_SALE_QTY
                                       , Y2025_SALE_PKG_QTY
                                       , Y2025_SALE_FAB_QTY
                                       , Y2025_SALE_EQ_QTY
                                       , Y2025_SALE_AMT
                                       , DECODE(Y2025_SALE_QTY, 0
                                              , 0
                                              , Y2025_SALE_AMT / Y2025_SALE_QTY) AS Y2025_SALE_ASP
                                       , DECODE(Y2025_SALE_PKG_QTY, 0
                                              , 0
                                              , Y2025_SALE_AMT / Y2025_SALE_PKG_QTY) AS Y2025_SALE_PKG_ASP
                                       , DECODE(Y2025_SALE_FAB_QTY, 0
                                              , 0
                                              , Y2025_SALE_AMT / Y2025_SALE_FAB_QTY) AS Y2025_SALE_FAB_ASP
                                       , DECODE(Y2025_SALE_EQ_QTY, 0
                                              , 0
                                              , Y2025_SALE_AMT / Y2025_SALE_EQ_QTY) AS Y2025_SALE_EQ_ASP
                                       , Y2025_INV_QTY
                                       , Y2025_INV_PKG_QTY
                                       , Y2025_INV_FAB_QTY
                                       , Y2025_INV_EQ_QTY
                                       , TOTAL_SALE_QTY
                                       , TOTAL_SALE_PKG_QTY
                                       , TOTAL_SALE_FAB_QTY
                                       , TOTAL_SALE_EQ_QTY
                                       , TOTAL_SALE_AMT
                                       , DECODE(TOTAL_SALE_QTY, 0
                                              , 0
                                              , TOTAL_SALE_AMT / TOTAL_SALE_QTY) AS TOTAL_SALE_ASP
                                       , DECODE(TOTAL_SALE_PKG_QTY, 0
                                              , 0
                                              , TOTAL_SALE_AMT / TOTAL_SALE_PKG_QTY) AS TOTAL_SALE_PKG_ASP
                                       , DECODE(TOTAL_SALE_FAB_QTY, 0
                                              , 0
                                              , TOTAL_SALE_AMT / TOTAL_SALE_FAB_QTY) AS TOTAL_SALE_FAB_ASP
                                       , DECODE(TOTAL_SALE_EQ_QTY, 0
                                              , 0
                                              , TOTAL_SALE_AMT / TOTAL_SALE_EQ_QTY) AS TOTAL_SALE_EQ_ASP
                                       , TOTAL_INV_QTY
                                       , TOTAL_INV_PKG_QTY
                                       , TOTAL_INV_FAB_QTY
                                       , TOTAL_INV_EQ_QTY
                                    FROM(
                                                SELECT
                                                       /* Dimension의 변형 */
                                                       NVL(SCM_FAMILY_CD, '*')     AS SCM_FAMILY_CD
                                                     , NVL(TECH_CD, '*')           AS TECH_CD
                                                     , NVL(FAB_DEN_CD, '*')        AS FAB_DEN_CD
                                                     , NVL(CHG_PROD_MODE_CD, '*')  AS CHG_PROD_MODE_CD
                                                     , NVL(CELL_LAYER_TYP_CD, '*') AS CELL_LAYER_TYP_CD
                                                     , PLN_REV
                                                       /* 월별  판매수량(원수량, PKG수량, FAB수량, EQ수량), 월별  ASP(원, PKG, FAB, EQ), 월별 판매금액, 월별 재고(원수량, PKG수량, FAB수량, EQ수량)를 횡(PIVOT)으로 조회*/
                                                       /* 월별  판매수량(원수량, PKG수량, FAB수량, EQ수량), 월별  ASP(원, PKG, FAB, EQ), 월별 판매금액, 월별 재고(원수량, PKG수량, FAB수량, EQ수량)로 */
                                                       /* 분기, 반기, 년 및 TOTAL의 집계데이터 생성 */
                                                     , M202401_SALE_QTY
                                                     , M202401_SALE_PKG_QTY
                                                     , M202401_SALE_FAB_QTY
                                                     , M202401_SALE_EQ_QTY
                                                     , M202401_SALE_ASP
                                                     , M202401_SALE_PKG_ASP
                                                     , M202401_SALE_FAB_ASP
                                                     , M202401_SALE_EQ_ASP
                                                     , M202401_SALE_AMT
                                                     , M202401_INV_QTY
                                                     , M202401_INV_PKG_QTY
                                                     , M202401_INV_FAB_QTY
                                                     , M202401_INV_EQ_QTY
                                                     , M202402_SALE_QTY
                                                     , M202402_SALE_PKG_QTY
                                                     , M202402_SALE_FAB_QTY
                                                     , M202402_SALE_EQ_QTY
                                                     , M202402_SALE_ASP
                                                     , M202402_SALE_PKG_ASP
                                                     , M202402_SALE_FAB_ASP
                                                     , M202402_SALE_EQ_ASP
                                                     , M202402_SALE_AMT
                                                     , M202402_INV_QTY
                                                     , M202402_INV_PKG_QTY
                                                     , M202402_INV_FAB_QTY
                                                     , M202402_INV_EQ_QTY
                                                     , M202403_SALE_QTY
                                                     , M202403_SALE_PKG_QTY
                                                     , M202403_SALE_FAB_QTY
                                                     , M202403_SALE_EQ_QTY
                                                     , M202403_SALE_ASP
                                                     , M202403_SALE_PKG_ASP
                                                     , M202403_SALE_FAB_ASP
                                                     , M202403_SALE_EQ_ASP
                                                     , M202403_SALE_AMT
                                                     , M202403_INV_QTY
                                                     , M202403_INV_PKG_QTY
                                                     , M202403_INV_FAB_QTY
                                                     , M202403_INV_EQ_QTY
                                                     , M202401_SALE_QTY     + M202402_SALE_QTY + M202403_SALE_QTY         AS Q202401_SALE_QTY
                                                     , M202401_SALE_PKG_QTY + M202402_SALE_PKG_QTY + M202403_SALE_PKG_QTY AS Q202401_SALE_PKG_QTY
                                                     , M202401_SALE_FAB_QTY + M202402_SALE_FAB_QTY + M202403_SALE_FAB_QTY AS Q202401_SALE_FAB_QTY
                                                     , M202401_SALE_EQ_QTY  + M202402_SALE_EQ_QTY + M202403_SALE_EQ_QTY   AS Q202401_SALE_EQ_QTY
                                                     , M202401_SALE_AMT     + M202402_SALE_AMT + M202403_SALE_AMT         AS Q202401_SALE_AMT
                                                     , M202403_INV_QTY                                                    AS Q202401_INV_QTY
                                                     , M202403_INV_PKG_QTY                                                AS Q202401_INV_PKG_QTY
                                                     , M202403_INV_FAB_QTY                                                AS Q202401_INV_FAB_QTY
                                                     , M202403_INV_EQ_QTY                                                 AS Q202401_INV_EQ_QTY
                                                     , M202404_SALE_QTY
                                                     , M202404_SALE_PKG_QTY
                                                     , M202404_SALE_FAB_QTY
                                                     , M202404_SALE_EQ_QTY
                                                     , M202404_SALE_ASP
                                                     , M202404_SALE_PKG_ASP
                                                     , M202404_SALE_FAB_ASP
                                                     , M202404_SALE_EQ_ASP
                                                     , M202404_SALE_AMT
                                                     , M202404_INV_QTY
                                                     , M202404_INV_PKG_QTY
                                                     , M202404_INV_FAB_QTY
                                                     , M202404_INV_EQ_QTY
                                                     , M202405_SALE_QTY
                                                     , M202405_SALE_PKG_QTY
                                                     , M202405_SALE_FAB_QTY
                                                     , M202405_SALE_EQ_QTY
                                                     , M202405_SALE_ASP
                                                     , M202405_SALE_PKG_ASP
                                                     , M202405_SALE_FAB_ASP
                                                     , M202405_SALE_EQ_ASP
                                                     , M202405_SALE_AMT
                                                     , M202405_INV_QTY
                                                     , M202405_INV_PKG_QTY
                                                     , M202405_INV_FAB_QTY
                                                     , M202405_INV_EQ_QTY
                                                     , M202406_SALE_QTY
                                                     , M202406_SALE_PKG_QTY
                                                     , M202406_SALE_FAB_QTY
                                                     , M202406_SALE_EQ_QTY
                                                     , M202406_SALE_ASP
                                                     , M202406_SALE_PKG_ASP
                                                     , M202406_SALE_FAB_ASP
                                                     , M202406_SALE_EQ_ASP
                                                     , M202406_SALE_AMT
                                                     , M202406_INV_QTY
                                                     , M202406_INV_PKG_QTY
                                                     , M202406_INV_FAB_QTY
                                                     , M202406_INV_EQ_QTY
                                                     , M202404_SALE_QTY     + M202405_SALE_QTY + M202406_SALE_QTY                                                                              AS Q202402_SALE_QTY
                                                     , M202404_SALE_PKG_QTY + M202405_SALE_PKG_QTY + M202406_SALE_PKG_QTY                                                                      AS Q202402_SALE_PKG_QTY
                                                     , M202404_SALE_FAB_QTY + M202405_SALE_FAB_QTY + M202406_SALE_FAB_QTY                                                                      AS Q202402_SALE_FAB_QTY
                                                     , M202404_SALE_EQ_QTY  + M202405_SALE_EQ_QTY + M202406_SALE_EQ_QTY                                                                        AS Q202402_SALE_EQ_QTY
                                                     , M202404_SALE_AMT     + M202405_SALE_AMT + M202406_SALE_AMT                                                                              AS Q202402_SALE_AMT
                                                     , M202406_INV_QTY                                                                                                                         AS Q202402_INV_QTY
                                                     , M202406_INV_PKG_QTY                                                                                                                     AS Q202402_INV_PKG_QTY
                                                     , M202406_INV_FAB_QTY                                                                                                                     AS Q202402_INV_FAB_QTY
                                                     , M202406_INV_EQ_QTY                                                                                                                      AS Q202402_INV_EQ_QTY
                                                     , M202401_SALE_QTY     + M202402_SALE_QTY + M202403_SALE_QTY + M202404_SALE_QTY + M202405_SALE_QTY + M202406_SALE_QTY                     AS H202401_SALE_QTY
                                                     , M202401_SALE_PKG_QTY + M202402_SALE_PKG_QTY + M202403_SALE_PKG_QTY + M202404_SALE_PKG_QTY + M202405_SALE_PKG_QTY + M202406_SALE_PKG_QTY AS H202401_SALE_PKG_QTY
                                                     , M202401_SALE_FAB_QTY + M202402_SALE_FAB_QTY + M202403_SALE_FAB_QTY + M202404_SALE_FAB_QTY + M202405_SALE_FAB_QTY + M202406_SALE_FAB_QTY AS H202401_SALE_FAB_QTY
                                                     , M202401_SALE_EQ_QTY  + M202402_SALE_EQ_QTY + M202403_SALE_EQ_QTY + M202404_SALE_EQ_QTY + M202405_SALE_EQ_QTY + M202406_SALE_EQ_QTY      AS H202401_SALE_EQ_QTY
                                                     , M202401_SALE_AMT     + M202402_SALE_AMT + M202403_SALE_AMT + M202404_SALE_AMT + M202405_SALE_AMT + M202406_SALE_AMT                     AS H202401_SALE_AMT
                                                     , M202406_INV_QTY                                                                                                                         AS H202401_INV_QTY
                                                     , M202406_INV_PKG_QTY                                                                                                                     AS H202401_INV_PKG_QTY
                                                     , M202406_INV_FAB_QTY                                                                                                                     AS H202401_INV_FAB_QTY
                                                     , M202406_INV_EQ_QTY                                                                                                                      AS H202401_INV_EQ_QTY
                                                     , M202407_SALE_QTY
                                                     , M202407_SALE_PKG_QTY
                                                     , M202407_SALE_FAB_QTY
                                                     , M202407_SALE_EQ_QTY
                                                     , M202407_SALE_ASP
                                                     , M202407_SALE_PKG_ASP
                                                     , M202407_SALE_FAB_ASP
                                                     , M202407_SALE_EQ_ASP
                                                     , M202407_SALE_AMT
                                                     , M202407_INV_QTY
                                                     , M202407_INV_PKG_QTY
                                                     , M202407_INV_FAB_QTY
                                                     , M202407_INV_EQ_QTY
                                                     , M202408_SALE_QTY
                                                     , M202408_SALE_PKG_QTY
                                                     , M202408_SALE_FAB_QTY
                                                     , M202408_SALE_EQ_QTY
                                                     , M202408_SALE_ASP
                                                     , M202408_SALE_PKG_ASP
                                                     , M202408_SALE_FAB_ASP
                                                     , M202408_SALE_EQ_ASP
                                                     , M202408_SALE_AMT
                                                     , M202408_INV_QTY
                                                     , M202408_INV_PKG_QTY
                                                     , M202408_INV_FAB_QTY
                                                     , M202408_INV_EQ_QTY
                                                     , M202409_SALE_QTY
                                                     , M202409_SALE_PKG_QTY
                                                     , M202409_SALE_FAB_QTY
                                                     , M202409_SALE_EQ_QTY
                                                     , M202409_SALE_ASP
                                                     , M202409_SALE_PKG_ASP
                                                     , M202409_SALE_FAB_ASP
                                                     , M202409_SALE_EQ_ASP
                                                     , M202409_SALE_AMT
                                                     , M202409_INV_QTY
                                                     , M202409_INV_PKG_QTY
                                                     , M202409_INV_FAB_QTY
                                                     , M202409_INV_EQ_QTY
                                                     , M202407_SALE_QTY     + M202408_SALE_QTY + M202409_SALE_QTY         AS Q202403_SALE_QTY
                                                     , M202407_SALE_PKG_QTY + M202408_SALE_PKG_QTY + M202409_SALE_PKG_QTY AS Q202403_SALE_PKG_QTY
                                                     , M202407_SALE_FAB_QTY + M202408_SALE_FAB_QTY + M202409_SALE_FAB_QTY AS Q202403_SALE_FAB_QTY
                                                     , M202407_SALE_EQ_QTY  + M202408_SALE_EQ_QTY + M202409_SALE_EQ_QTY   AS Q202403_SALE_EQ_QTY
                                                     , M202407_SALE_AMT     + M202408_SALE_AMT + M202409_SALE_AMT         AS Q202403_SALE_AMT
                                                     , M202409_INV_QTY                                                    AS Q202403_INV_QTY
                                                     , M202409_INV_PKG_QTY                                                AS Q202403_INV_PKG_QTY
                                                     , M202409_INV_FAB_QTY                                                AS Q202403_INV_FAB_QTY
                                                     , M202409_INV_EQ_QTY                                                 AS Q202403_INV_EQ_QTY
                                                     , M202410_SALE_QTY
                                                     , M202410_SALE_PKG_QTY
                                                     , M202410_SALE_FAB_QTY
                                                     , M202410_SALE_EQ_QTY
                                                     , M202410_SALE_ASP
                                                     , M202410_SALE_PKG_ASP
                                                     , M202410_SALE_FAB_ASP
                                                     , M202410_SALE_EQ_ASP
                                                     , M202410_SALE_AMT
                                                     , M202410_INV_QTY
                                                     , M202410_INV_PKG_QTY
                                                     , M202410_INV_FAB_QTY
                                                     , M202410_INV_EQ_QTY
                                                     , M202411_SALE_QTY
                                                     , M202411_SALE_PKG_QTY
                                                     , M202411_SALE_FAB_QTY
                                                     , M202411_SALE_EQ_QTY
                                                     , M202411_SALE_ASP
                                                     , M202411_SALE_PKG_ASP
                                                     , M202411_SALE_FAB_ASP
                                                     , M202411_SALE_EQ_ASP
                                                     , M202411_SALE_AMT
                                                     , M202411_INV_QTY
                                                     , M202411_INV_PKG_QTY
                                                     , M202411_INV_FAB_QTY
                                                     , M202411_INV_EQ_QTY
                                                     , M202412_SALE_QTY
                                                     , M202412_SALE_PKG_QTY
                                                     , M202412_SALE_FAB_QTY
                                                     , M202412_SALE_EQ_QTY
                                                     , M202412_SALE_ASP
                                                     , M202412_SALE_PKG_ASP
                                                     , M202412_SALE_FAB_ASP
                                                     , M202412_SALE_EQ_ASP
                                                     , M202412_SALE_AMT
                                                     , M202412_INV_QTY
                                                     , M202412_INV_PKG_QTY
                                                     , M202412_INV_FAB_QTY
                                                     , M202412_INV_EQ_QTY
                                                     , M202410_SALE_QTY     + M202411_SALE_QTY + M202412_SALE_QTY                                                                                                                                                                                                        AS Q202404_SALE_QTY
                                                     , M202410_SALE_PKG_QTY + M202411_SALE_PKG_QTY + M202412_SALE_PKG_QTY                                                                                                                                                                                                        AS Q202404_SALE_PKG_QTY
                                                     , M202410_SALE_FAB_QTY + M202411_SALE_FAB_QTY + M202412_SALE_FAB_QTY                                                                                                                                                                                                        AS Q202404_SALE_FAB_QTY
                                                     , M202410_SALE_EQ_QTY  + M202411_SALE_EQ_QTY + M202412_SALE_EQ_QTY                                                                                                                                                                                                        AS Q202404_SALE_EQ_QTY
                                                     , M202410_SALE_AMT     + M202411_SALE_AMT + M202412_SALE_AMT                                                                                                                                                                                                        AS Q202404_SALE_AMT
                                                     , M202412_INV_QTY                                                                                                                                                                                                        AS Q202404_INV_QTY
                                                     , M202412_INV_PKG_QTY                                                                                                                                                                                                        AS Q202404_INV_PKG_QTY
                                                     , M202412_INV_FAB_QTY                                                                                                                                                                                                        AS Q202404_INV_FAB_QTY
                                                     , M202412_INV_EQ_QTY                                                                                                                                                                                                        AS Q202404_INV_EQ_QTY
                                                     , M202407_SALE_QTY     + M202408_SALE_QTY + M202409_SALE_QTY + M202410_SALE_QTY + M202411_SALE_QTY + M202412_SALE_QTY                                                                                                                                                               AS H202402_SALE_QTY
                                                     , M202407_SALE_PKG_QTY + M202408_SALE_PKG_QTY + M202409_SALE_PKG_QTY + M202410_SALE_PKG_QTY + M202411_SALE_PKG_QTY + M202412_SALE_PKG_QTY                                                                                                                                           AS H202402_SALE_PKG_QTY
                                                     , M202407_SALE_FAB_QTY + M202408_SALE_FAB_QTY + M202409_SALE_FAB_QTY + M202410_SALE_FAB_QTY + M202411_SALE_FAB_QTY + M202412_SALE_FAB_QTY                                                                                                                                           AS H202402_SALE_FAB_QTY
                                                     , M202407_SALE_EQ_QTY  + M202408_SALE_EQ_QTY + M202409_SALE_EQ_QTY + M202410_SALE_EQ_QTY + M202411_SALE_EQ_QTY + M202412_SALE_EQ_QTY                                                                                                                                                AS H202402_SALE_EQ_QTY
                                                     , M202407_SALE_AMT     + M202408_SALE_AMT + M202409_SALE_AMT + M202410_SALE_AMT + M202411_SALE_AMT + M202412_SALE_AMT                                                                                                                                                               AS H202402_SALE_AMT
                                                     , M202412_INV_QTY                                                                                                                                                                                                        AS H202402_INV_QTY
                                                     , M202412_INV_PKG_QTY                                                                                                                                                                                                        AS H202402_INV_PKG_QTY
                                                     , M202412_INV_FAB_QTY                                                                                                                                                                                                        AS H202402_INV_FAB_QTY
                                                     , M202412_INV_EQ_QTY                                                                                                                                                                                                        AS H202402_INV_EQ_QTY
                                                     , M202401_SALE_QTY     + M202402_SALE_QTY + M202403_SALE_QTY + M202404_SALE_QTY + M202405_SALE_QTY + M202406_SALE_QTY + M202407_SALE_QTY + M202408_SALE_QTY + M202409_SALE_QTY + M202410_SALE_QTY + M202411_SALE_QTY + M202412_SALE_QTY                                             AS Y2024_SALE_QTY
                                                     , M202401_SALE_PKG_QTY + M202402_SALE_PKG_QTY + M202403_SALE_PKG_QTY + M202404_SALE_PKG_QTY + M202405_SALE_PKG_QTY + M202406_SALE_PKG_QTY + M202407_SALE_PKG_QTY + M202408_SALE_PKG_QTY + M202409_SALE_PKG_QTY + M202410_SALE_PKG_QTY + M202411_SALE_PKG_QTY + M202412_SALE_PKG_QTY AS Y2024_SALE_PKG_QTY
                                                     , M202401_SALE_FAB_QTY + M202402_SALE_FAB_QTY + M202403_SALE_FAB_QTY + M202404_SALE_FAB_QTY + M202405_SALE_FAB_QTY + M202406_SALE_FAB_QTY + M202407_SALE_FAB_QTY + M202408_SALE_FAB_QTY + M202409_SALE_FAB_QTY + M202410_SALE_FAB_QTY + M202411_SALE_FAB_QTY + M202412_SALE_FAB_QTY AS Y2024_SALE_FAB_QTY
                                                     , M202401_SALE_EQ_QTY  + M202402_SALE_EQ_QTY + M202403_SALE_EQ_QTY + M202404_SALE_EQ_QTY + M202405_SALE_EQ_QTY + M202406_SALE_EQ_QTY + M202407_SALE_EQ_QTY + M202408_SALE_EQ_QTY + M202409_SALE_EQ_QTY + M202410_SALE_EQ_QTY + M202411_SALE_EQ_QTY + M202412_SALE_EQ_QTY            AS Y2024_SALE_EQ_QTY
                                                     , M202401_SALE_AMT     + M202402_SALE_AMT + M202403_SALE_AMT + M202404_SALE_AMT + M202405_SALE_AMT + M202406_SALE_AMT + M202407_SALE_AMT + M202408_SALE_AMT + M202409_SALE_AMT + M202410_SALE_AMT + M202411_SALE_AMT + M202412_SALE_AMT                                             AS Y2024_SALE_AMT
                                                     , M202412_INV_QTY                                                                                                                                                                                                        AS Y2024_INV_QTY
                                                     , M202412_INV_PKG_QTY                                                                                                                                                                                                        AS Y2024_INV_PKG_QTY
                                                     , M202412_INV_FAB_QTY                                                                                                                                                                                                        AS Y2024_INV_FAB_QTY
                                                     , M202412_INV_EQ_QTY                                                                                                                                                                                                        AS Y2024_INV_EQ_QTY
                                                     , M202501_SALE_QTY
                                                     , M202501_SALE_PKG_QTY
                                                     , M202501_SALE_FAB_QTY
                                                     , M202501_SALE_EQ_QTY
                                                     , M202501_SALE_ASP
                                                     , M202501_SALE_PKG_ASP
                                                     , M202501_SALE_FAB_ASP
                                                     , M202501_SALE_EQ_ASP
                                                     , M202501_SALE_AMT
                                                     , M202501_INV_QTY
                                                     , M202501_INV_PKG_QTY
                                                     , M202501_INV_FAB_QTY
                                                     , M202501_INV_EQ_QTY
                                                     , M202502_SALE_QTY
                                                     , M202502_SALE_PKG_QTY
                                                     , M202502_SALE_FAB_QTY
                                                     , M202502_SALE_EQ_QTY
                                                     , M202502_SALE_ASP
                                                     , M202502_SALE_PKG_ASP
                                                     , M202502_SALE_FAB_ASP
                                                     , M202502_SALE_EQ_ASP
                                                     , M202502_SALE_AMT
                                                     , M202502_INV_QTY
                                                     , M202502_INV_PKG_QTY
                                                     , M202502_INV_FAB_QTY
                                                     , M202502_INV_EQ_QTY
                                                     , M202503_SALE_QTY
                                                     , M202503_SALE_PKG_QTY
                                                     , M202503_SALE_FAB_QTY
                                                     , M202503_SALE_EQ_QTY
                                                     , M202503_SALE_ASP
                                                     , M202503_SALE_PKG_ASP
                                                     , M202503_SALE_FAB_ASP
                                                     , M202503_SALE_EQ_ASP
                                                     , M202503_SALE_AMT
                                                     , M202503_INV_QTY
                                                     , M202503_INV_PKG_QTY
                                                     , M202503_INV_FAB_QTY
                                                     , M202503_INV_EQ_QTY
                                                     , M202501_SALE_QTY     + M202502_SALE_QTY + M202503_SALE_QTY         AS Q202501_SALE_QTY
                                                     , M202501_SALE_PKG_QTY + M202502_SALE_PKG_QTY + M202503_SALE_PKG_QTY AS Q202501_SALE_PKG_QTY
                                                     , M202501_SALE_FAB_QTY + M202502_SALE_FAB_QTY + M202503_SALE_FAB_QTY AS Q202501_SALE_FAB_QTY
                                                     , M202501_SALE_EQ_QTY  + M202502_SALE_EQ_QTY + M202503_SALE_EQ_QTY   AS Q202501_SALE_EQ_QTY
                                                     , M202501_SALE_AMT     + M202502_SALE_AMT + M202503_SALE_AMT         AS Q202501_SALE_AMT
                                                     , M202503_INV_QTY                                                    AS Q202501_INV_QTY
                                                     , M202503_INV_PKG_QTY                                                AS Q202501_INV_PKG_QTY
                                                     , M202503_INV_FAB_QTY                                                AS Q202501_INV_FAB_QTY
                                                     , M202503_INV_EQ_QTY                                                 AS Q202501_INV_EQ_QTY
                                                     , M202504_SALE_QTY
                                                     , M202504_SALE_PKG_QTY
                                                     , M202504_SALE_FAB_QTY
                                                     , M202504_SALE_EQ_QTY
                                                     , M202504_SALE_ASP
                                                     , M202504_SALE_PKG_ASP
                                                     , M202504_SALE_FAB_ASP
                                                     , M202504_SALE_EQ_ASP
                                                     , M202504_SALE_AMT
                                                     , M202504_INV_QTY
                                                     , M202504_INV_PKG_QTY
                                                     , M202504_INV_FAB_QTY
                                                     , M202504_INV_EQ_QTY
                                                     , M202504_SALE_QTY                                                                                                                                                                                                        AS Q202502_SALE_QTY
                                                     , M202504_SALE_PKG_QTY                                                                                                                                                                                                        AS Q202502_SALE_PKG_QTY
                                                     , M202504_SALE_FAB_QTY                                                                                                                                                                                                        AS Q202502_SALE_FAB_QTY
                                                     , M202504_SALE_EQ_QTY                                                                                                                                                                                                        AS Q202502_SALE_EQ_QTY
                                                     , M202504_SALE_AMT                                                                                                                                                                                                        AS Q202502_SALE_AMT
                                                     , M202504_INV_QTY                                                                                                                                                                                                        AS Q202502_INV_QTY
                                                     , M202504_INV_PKG_QTY                                                                                                                                                                                                        AS Q202502_INV_PKG_QTY
                                                     , M202504_INV_FAB_QTY                                                                                                                                                                                                        AS Q202502_INV_FAB_QTY
                                                     , M202504_INV_EQ_QTY                                                                                                                                                                                                        AS Q202502_INV_EQ_QTY
                                                     , M202501_SALE_QTY     + M202502_SALE_QTY + M202503_SALE_QTY + M202504_SALE_QTY                                                                                                                                                                                                        AS H202501_SALE_QTY
                                                     , M202501_SALE_PKG_QTY + M202502_SALE_PKG_QTY + M202503_SALE_PKG_QTY + M202504_SALE_PKG_QTY                                                                                                                                                                                                        AS H202501_SALE_PKG_QTY
                                                     , M202501_SALE_FAB_QTY + M202502_SALE_FAB_QTY + M202503_SALE_FAB_QTY + M202504_SALE_FAB_QTY                                                                                                                                                                                                        AS H202501_SALE_FAB_QTY
                                                     , M202501_SALE_EQ_QTY  + M202502_SALE_EQ_QTY + M202503_SALE_EQ_QTY + M202504_SALE_EQ_QTY                                                                                                                                                                                                        AS H202501_SALE_EQ_QTY
                                                     , M202501_SALE_AMT     + M202502_SALE_AMT + M202503_SALE_AMT + M202504_SALE_AMT                                                                                                                                                                                                        AS H202501_SALE_AMT
                                                     , M202504_INV_QTY                                                                                                                                                                                                        AS H202501_INV_QTY
                                                     , M202504_INV_PKG_QTY                                                                                                                                                                                                        AS H202501_INV_PKG_QTY
                                                     , M202504_INV_FAB_QTY                                                                                                                                                                                                        AS H202501_INV_FAB_QTY
                                                     , M202504_INV_EQ_QTY                                                                                                                                                                                                        AS H202501_INV_EQ_QTY
                                                     , M202501_SALE_QTY     + M202502_SALE_QTY + M202503_SALE_QTY + M202504_SALE_QTY                                                                                                                                                                                                        AS Y2025_SALE_QTY
                                                     , M202501_SALE_PKG_QTY + M202502_SALE_PKG_QTY + M202503_SALE_PKG_QTY + M202504_SALE_PKG_QTY                                                                                                                                                                                                        AS Y2025_SALE_PKG_QTY
                                                     , M202501_SALE_FAB_QTY + M202502_SALE_FAB_QTY + M202503_SALE_FAB_QTY + M202504_SALE_FAB_QTY                                                                                                                                                                                                        AS Y2025_SALE_FAB_QTY
                                                     , M202501_SALE_EQ_QTY  + M202502_SALE_EQ_QTY + M202503_SALE_EQ_QTY + M202504_SALE_EQ_QTY                                                                                                                                                                                                        AS Y2025_SALE_EQ_QTY
                                                     , M202501_SALE_AMT     + M202502_SALE_AMT + M202503_SALE_AMT + M202504_SALE_AMT                                                                                                                                                                                                        AS Y2025_SALE_AMT
                                                     , M202504_INV_QTY                                                                                                                                                                                                        AS Y2025_INV_QTY
                                                     , M202504_INV_PKG_QTY                                                                                                                                                                                                        AS Y2025_INV_PKG_QTY
                                                     , M202504_INV_FAB_QTY                                                                                                                                                                                                        AS Y2025_INV_FAB_QTY
                                                     , M202504_INV_EQ_QTY                                                                                                                                                                                                        AS Y2025_INV_EQ_QTY
                                                     , M202401_SALE_QTY     + M202402_SALE_QTY + M202403_SALE_QTY + M202404_SALE_QTY + M202405_SALE_QTY + M202406_SALE_QTY + M202407_SALE_QTY + M202408_SALE_QTY + M202409_SALE_QTY + M202410_SALE_QTY + M202411_SALE_QTY + M202412_SALE_QTY + M202501_SALE_QTY + M202502_SALE_QTY + M202503_SALE_QTY + M202504_SALE_QTY                                                             AS TOTAL_SALE_QTY
                                                     , M202401_SALE_PKG_QTY + M202402_SALE_PKG_QTY + M202403_SALE_PKG_QTY + M202404_SALE_PKG_QTY + M202405_SALE_PKG_QTY + M202406_SALE_PKG_QTY + M202407_SALE_PKG_QTY + M202408_SALE_PKG_QTY + M202409_SALE_PKG_QTY + M202410_SALE_PKG_QTY + M202411_SALE_PKG_QTY + M202412_SALE_PKG_QTY + M202501_SALE_PKG_QTY + M202502_SALE_PKG_QTY + M202503_SALE_PKG_QTY + M202504_SALE_PKG_QTY AS TOTAL_SALE_PKG_QTY
                                                     , M202401_SALE_FAB_QTY + M202402_SALE_FAB_QTY + M202403_SALE_FAB_QTY + M202404_SALE_FAB_QTY + M202405_SALE_FAB_QTY + M202406_SALE_FAB_QTY + M202407_SALE_FAB_QTY + M202408_SALE_FAB_QTY + M202409_SALE_FAB_QTY + M202410_SALE_FAB_QTY + M202411_SALE_FAB_QTY + M202412_SALE_FAB_QTY + M202501_SALE_FAB_QTY + M202502_SALE_FAB_QTY + M202503_SALE_FAB_QTY + M202504_SALE_FAB_QTY AS TOTAL_SALE_FAB_QTY
                                                     , M202401_SALE_EQ_QTY  + M202402_SALE_EQ_QTY + M202403_SALE_EQ_QTY + M202404_SALE_EQ_QTY + M202405_SALE_EQ_QTY + M202406_SALE_EQ_QTY + M202407_SALE_EQ_QTY + M202408_SALE_EQ_QTY + M202409_SALE_EQ_QTY + M202410_SALE_EQ_QTY + M202411_SALE_EQ_QTY + M202412_SALE_EQ_QTY + M202501_SALE_EQ_QTY + M202502_SALE_EQ_QTY + M202503_SALE_EQ_QTY + M202504_SALE_EQ_QTY                AS TOTAL_SALE_EQ_QTY
                                                     , M202401_SALE_AMT     + M202402_SALE_AMT + M202403_SALE_AMT + M202404_SALE_AMT + M202405_SALE_AMT + M202406_SALE_AMT + M202407_SALE_AMT + M202408_SALE_AMT + M202409_SALE_AMT + M202410_SALE_AMT + M202411_SALE_AMT + M202412_SALE_AMT + M202501_SALE_AMT + M202502_SALE_AMT + M202503_SALE_AMT + M202504_SALE_AMT                                                             AS TOTAL_SALE_AMT
                                                     , M202504_INV_QTY                                                                                                                                                                                                        AS TOTAL_INV_QTY
                                                     , M202504_INV_PKG_QTY                                                                                                                                                                                                        AS TOTAL_INV_PKG_QTY
                                                     , M202504_INV_FAB_QTY                                                                                                                                                                                                        AS TOTAL_INV_FAB_QTY
                                                     , M202504_INV_EQ_QTY                                                                                                                                                                                                        AS TOTAL_INV_EQ_QTY
                                                  FROM(
                                                              SELECT SCM_FAMILY_CD
                                                                   , TECH_CD
                                                                   , FAB_DEN_CD
                                                                   , CHG_PROD_MODE_CD
                                                                   , CELL_LAYER_TYP_CD
                                                                   , PLN_REV
                                                                     /* 월별  판매수량(원수량, PKG수량, FAB수량, EQ수량), 월별  ASP(원, PKG, FAB, EQ), 월별 판매금액, 월별 재고(원수량, PKG수량, FAB수량, EQ수량)를 횡(PIVOT)으로 조회*/
                                                                   , NVL(M202401_SALE_QTY, 0)     AS M202401_SALE_QTY
                                                                   , NVL(M202401_SALE_PKG_QTY, 0) AS M202401_SALE_PKG_QTY
                                                                   , NVL(M202401_SALE_FAB_QTY, 0) AS M202401_SALE_FAB_QTY
                                                                   , NVL(M202401_SALE_EQ_QTY, 0)  AS M202401_SALE_EQ_QTY
                                                                   , NVL(M202401_SALE_ASP, 0)     AS M202401_SALE_ASP
                                                                   , NVL(M202401_SALE_PKG_ASP, 0) AS M202401_SALE_PKG_ASP
                                                                   , NVL(M202401_SALE_FAB_ASP, 0) AS M202401_SALE_FAB_ASP
                                                                   , NVL(M202401_SALE_EQ_ASP, 0)  AS M202401_SALE_EQ_ASP
                                                                   , NVL(M202401_SALE_AMT, 0)     AS M202401_SALE_AMT
                                                                   , NVL(M202401_INV_QTY, 0)      AS M202401_INV_QTY
                                                                   , NVL(M202401_INV_PKG_QTY, 0)  AS M202401_INV_PKG_QTY
                                                                   , NVL(M202401_INV_FAB_QTY, 0)  AS M202401_INV_FAB_QTY
                                                                   , NVL(M202401_INV_EQ_QTY, 0)   AS M202401_INV_EQ_QTY
                                                                   , NVL(M202402_SALE_QTY, 0)     AS M202402_SALE_QTY
                                                                   , NVL(M202402_SALE_PKG_QTY, 0) AS M202402_SALE_PKG_QTY
                                                                   , NVL(M202402_SALE_FAB_QTY, 0) AS M202402_SALE_FAB_QTY
                                                                   , NVL(M202402_SALE_EQ_QTY, 0)  AS M202402_SALE_EQ_QTY
                                                                   , NVL(M202402_SALE_ASP, 0)     AS M202402_SALE_ASP
                                                                   , NVL(M202402_SALE_PKG_ASP, 0) AS M202402_SALE_PKG_ASP
                                                                   , NVL(M202402_SALE_FAB_ASP, 0) AS M202402_SALE_FAB_ASP
                                                                   , NVL(M202402_SALE_EQ_ASP, 0)  AS M202402_SALE_EQ_ASP
                                                                   , NVL(M202402_SALE_AMT, 0)     AS M202402_SALE_AMT
                                                                   , NVL(M202402_INV_QTY, 0)      AS M202402_INV_QTY
                                                                   , NVL(M202402_INV_PKG_QTY, 0)  AS M202402_INV_PKG_QTY
                                                                   , NVL(M202402_INV_FAB_QTY, 0)  AS M202402_INV_FAB_QTY
                                                                   , NVL(M202402_INV_EQ_QTY, 0)   AS M202402_INV_EQ_QTY
                                                                   , NVL(M202403_SALE_QTY, 0)     AS M202403_SALE_QTY
                                                                   , NVL(M202403_SALE_PKG_QTY, 0) AS M202403_SALE_PKG_QTY
                                                                   , NVL(M202403_SALE_FAB_QTY, 0) AS M202403_SALE_FAB_QTY
                                                                   , NVL(M202403_SALE_EQ_QTY, 0)  AS M202403_SALE_EQ_QTY
                                                                   , NVL(M202403_SALE_ASP, 0)     AS M202403_SALE_ASP
                                                                   , NVL(M202403_SALE_PKG_ASP, 0) AS M202403_SALE_PKG_ASP
                                                                   , NVL(M202403_SALE_FAB_ASP, 0) AS M202403_SALE_FAB_ASP
                                                                   , NVL(M202403_SALE_EQ_ASP, 0)  AS M202403_SALE_EQ_ASP
                                                                   , NVL(M202403_SALE_AMT, 0)     AS M202403_SALE_AMT
                                                                   , NVL(M202403_INV_QTY, 0)      AS M202403_INV_QTY
                                                                   , NVL(M202403_INV_PKG_QTY, 0)  AS M202403_INV_PKG_QTY
                                                                   , NVL(M202403_INV_FAB_QTY, 0)  AS M202403_INV_FAB_QTY
                                                                   , NVL(M202403_INV_EQ_QTY, 0)   AS M202403_INV_EQ_QTY
                                                                   , NVL(M202404_SALE_QTY, 0)     AS M202404_SALE_QTY
                                                                   , NVL(M202404_SALE_PKG_QTY, 0) AS M202404_SALE_PKG_QTY
                                                                   , NVL(M202404_SALE_FAB_QTY, 0) AS M202404_SALE_FAB_QTY
                                                                   , NVL(M202404_SALE_EQ_QTY, 0)  AS M202404_SALE_EQ_QTY
                                                                   , NVL(M202404_SALE_ASP, 0)     AS M202404_SALE_ASP
                                                                   , NVL(M202404_SALE_PKG_ASP, 0) AS M202404_SALE_PKG_ASP
                                                                   , NVL(M202404_SALE_FAB_ASP, 0) AS M202404_SALE_FAB_ASP
                                                                   , NVL(M202404_SALE_EQ_ASP, 0)  AS M202404_SALE_EQ_ASP
                                                                   , NVL(M202404_SALE_AMT, 0)     AS M202404_SALE_AMT
                                                                   , NVL(M202404_INV_QTY, 0)      AS M202404_INV_QTY
                                                                   , NVL(M202404_INV_PKG_QTY, 0)  AS M202404_INV_PKG_QTY
                                                                   , NVL(M202404_INV_FAB_QTY, 0)  AS M202404_INV_FAB_QTY
                                                                   , NVL(M202404_INV_EQ_QTY, 0)   AS M202404_INV_EQ_QTY
                                                                   , NVL(M202405_SALE_QTY, 0)     AS M202405_SALE_QTY
                                                                   , NVL(M202405_SALE_PKG_QTY, 0) AS M202405_SALE_PKG_QTY
                                                                   , NVL(M202405_SALE_FAB_QTY, 0) AS M202405_SALE_FAB_QTY
                                                                   , NVL(M202405_SALE_EQ_QTY, 0)  AS M202405_SALE_EQ_QTY
                                                                   , NVL(M202405_SALE_ASP, 0)     AS M202405_SALE_ASP
                                                                   , NVL(M202405_SALE_PKG_ASP, 0) AS M202405_SALE_PKG_ASP
                                                                   , NVL(M202405_SALE_FAB_ASP, 0) AS M202405_SALE_FAB_ASP
                                                                   , NVL(M202405_SALE_EQ_ASP, 0)  AS M202405_SALE_EQ_ASP
                                                                   , NVL(M202405_SALE_AMT, 0)     AS M202405_SALE_AMT
                                                                   , NVL(M202405_INV_QTY, 0)      AS M202405_INV_QTY
                                                                   , NVL(M202405_INV_PKG_QTY, 0)  AS M202405_INV_PKG_QTY
                                                                   , NVL(M202405_INV_FAB_QTY, 0)  AS M202405_INV_FAB_QTY
                                                                   , NVL(M202405_INV_EQ_QTY, 0)   AS M202405_INV_EQ_QTY
                                                                   , NVL(M202406_SALE_QTY, 0)     AS M202406_SALE_QTY
                                                                   , NVL(M202406_SALE_PKG_QTY, 0) AS M202406_SALE_PKG_QTY
                                                                   , NVL(M202406_SALE_FAB_QTY, 0) AS M202406_SALE_FAB_QTY
                                                                   , NVL(M202406_SALE_EQ_QTY, 0)  AS M202406_SALE_EQ_QTY
                                                                   , NVL(M202406_SALE_ASP, 0)     AS M202406_SALE_ASP
                                                                   , NVL(M202406_SALE_PKG_ASP, 0) AS M202406_SALE_PKG_ASP
                                                                   , NVL(M202406_SALE_FAB_ASP, 0) AS M202406_SALE_FAB_ASP
                                                                   , NVL(M202406_SALE_EQ_ASP, 0)  AS M202406_SALE_EQ_ASP
                                                                   , NVL(M202406_SALE_AMT, 0)     AS M202406_SALE_AMT
                                                                   , NVL(M202406_INV_QTY, 0)      AS M202406_INV_QTY
                                                                   , NVL(M202406_INV_PKG_QTY, 0)  AS M202406_INV_PKG_QTY
                                                                   , NVL(M202406_INV_FAB_QTY, 0)  AS M202406_INV_FAB_QTY
                                                                   , NVL(M202406_INV_EQ_QTY, 0)   AS M202406_INV_EQ_QTY
                                                                   , NVL(M202407_SALE_QTY, 0)     AS M202407_SALE_QTY
                                                                   , NVL(M202407_SALE_PKG_QTY, 0) AS M202407_SALE_PKG_QTY
                                                                   , NVL(M202407_SALE_FAB_QTY, 0) AS M202407_SALE_FAB_QTY
                                                                   , NVL(M202407_SALE_EQ_QTY, 0)  AS M202407_SALE_EQ_QTY
                                                                   , NVL(M202407_SALE_ASP, 0)     AS M202407_SALE_ASP
                                                                   , NVL(M202407_SALE_PKG_ASP, 0) AS M202407_SALE_PKG_ASP
                                                                   , NVL(M202407_SALE_FAB_ASP, 0) AS M202407_SALE_FAB_ASP
                                                                   , NVL(M202407_SALE_EQ_ASP, 0)  AS M202407_SALE_EQ_ASP
                                                                   , NVL(M202407_SALE_AMT, 0)     AS M202407_SALE_AMT
                                                                   , NVL(M202407_INV_QTY, 0)      AS M202407_INV_QTY
                                                                   , NVL(M202407_INV_PKG_QTY, 0)  AS M202407_INV_PKG_QTY
                                                                   , NVL(M202407_INV_FAB_QTY, 0)  AS M202407_INV_FAB_QTY
                                                                   , NVL(M202407_INV_EQ_QTY, 0)   AS M202407_INV_EQ_QTY
                                                                   , NVL(M202408_SALE_QTY, 0)     AS M202408_SALE_QTY
                                                                   , NVL(M202408_SALE_PKG_QTY, 0) AS M202408_SALE_PKG_QTY
                                                                   , NVL(M202408_SALE_FAB_QTY, 0) AS M202408_SALE_FAB_QTY
                                                                   , NVL(M202408_SALE_EQ_QTY, 0)  AS M202408_SALE_EQ_QTY
                                                                   , NVL(M202408_SALE_ASP, 0)     AS M202408_SALE_ASP
                                                                   , NVL(M202408_SALE_PKG_ASP, 0) AS M202408_SALE_PKG_ASP
                                                                   , NVL(M202408_SALE_FAB_ASP, 0) AS M202408_SALE_FAB_ASP
                                                                   , NVL(M202408_SALE_EQ_ASP, 0)  AS M202408_SALE_EQ_ASP
                                                                   , NVL(M202408_SALE_AMT, 0)     AS M202408_SALE_AMT
                                                                   , NVL(M202408_INV_QTY, 0)      AS M202408_INV_QTY
                                                                   , NVL(M202408_INV_PKG_QTY, 0)  AS M202408_INV_PKG_QTY
                                                                   , NVL(M202408_INV_FAB_QTY, 0)  AS M202408_INV_FAB_QTY
                                                                   , NVL(M202408_INV_EQ_QTY, 0)   AS M202408_INV_EQ_QTY
                                                                   , NVL(M202409_SALE_QTY, 0)     AS M202409_SALE_QTY
                                                                   , NVL(M202409_SALE_PKG_QTY, 0) AS M202409_SALE_PKG_QTY
                                                                   , NVL(M202409_SALE_FAB_QTY, 0) AS M202409_SALE_FAB_QTY
                                                                   , NVL(M202409_SALE_EQ_QTY, 0)  AS M202409_SALE_EQ_QTY
                                                                   , NVL(M202409_SALE_ASP, 0)     AS M202409_SALE_ASP
                                                                   , NVL(M202409_SALE_PKG_ASP, 0) AS M202409_SALE_PKG_ASP
                                                                   , NVL(M202409_SALE_FAB_ASP, 0) AS M202409_SALE_FAB_ASP
                                                                   , NVL(M202409_SALE_EQ_ASP, 0)  AS M202409_SALE_EQ_ASP
                                                                   , NVL(M202409_SALE_AMT, 0)     AS M202409_SALE_AMT
                                                                   , NVL(M202409_INV_QTY, 0)      AS M202409_INV_QTY
                                                                   , NVL(M202409_INV_PKG_QTY, 0)  AS M202409_INV_PKG_QTY
                                                                   , NVL(M202409_INV_FAB_QTY, 0)  AS M202409_INV_FAB_QTY
                                                                   , NVL(M202409_INV_EQ_QTY, 0)   AS M202409_INV_EQ_QTY
                                                                   , NVL(M202410_SALE_QTY, 0)     AS M202410_SALE_QTY
                                                                   , NVL(M202410_SALE_PKG_QTY, 0) AS M202410_SALE_PKG_QTY
                                                                   , NVL(M202410_SALE_FAB_QTY, 0) AS M202410_SALE_FAB_QTY
                                                                   , NVL(M202410_SALE_EQ_QTY, 0)  AS M202410_SALE_EQ_QTY
                                                                   , NVL(M202410_SALE_ASP, 0)     AS M202410_SALE_ASP
                                                                   , NVL(M202410_SALE_PKG_ASP, 0) AS M202410_SALE_PKG_ASP
                                                                   , NVL(M202410_SALE_FAB_ASP, 0) AS M202410_SALE_FAB_ASP
                                                                   , NVL(M202410_SALE_EQ_ASP, 0)  AS M202410_SALE_EQ_ASP
                                                                   , NVL(M202410_SALE_AMT, 0)     AS M202410_SALE_AMT
                                                                   , NVL(M202410_INV_QTY, 0)      AS M202410_INV_QTY
                                                                   , NVL(M202410_INV_PKG_QTY, 0)  AS M202410_INV_PKG_QTY
                                                                   , NVL(M202410_INV_FAB_QTY, 0)  AS M202410_INV_FAB_QTY
                                                                   , NVL(M202410_INV_EQ_QTY, 0)   AS M202410_INV_EQ_QTY
                                                                   , NVL(M202411_SALE_QTY, 0)     AS M202411_SALE_QTY
                                                                   , NVL(M202411_SALE_PKG_QTY, 0) AS M202411_SALE_PKG_QTY
                                                                   , NVL(M202411_SALE_FAB_QTY, 0) AS M202411_SALE_FAB_QTY
                                                                   , NVL(M202411_SALE_EQ_QTY, 0)  AS M202411_SALE_EQ_QTY
                                                                   , NVL(M202411_SALE_ASP, 0)     AS M202411_SALE_ASP
                                                                   , NVL(M202411_SALE_PKG_ASP, 0) AS M202411_SALE_PKG_ASP
                                                                   , NVL(M202411_SALE_FAB_ASP, 0) AS M202411_SALE_FAB_ASP
                                                                   , NVL(M202411_SALE_EQ_ASP, 0)  AS M202411_SALE_EQ_ASP
                                                                   , NVL(M202411_SALE_AMT, 0)     AS M202411_SALE_AMT
                                                                   , NVL(M202411_INV_QTY, 0)      AS M202411_INV_QTY
                                                                   , NVL(M202411_INV_PKG_QTY, 0)  AS M202411_INV_PKG_QTY
                                                                   , NVL(M202411_INV_FAB_QTY, 0)  AS M202411_INV_FAB_QTY
                                                                   , NVL(M202411_INV_EQ_QTY, 0)   AS M202411_INV_EQ_QTY
                                                                   , NVL(M202412_SALE_QTY, 0)     AS M202412_SALE_QTY
                                                                   , NVL(M202412_SALE_PKG_QTY, 0) AS M202412_SALE_PKG_QTY
                                                                   , NVL(M202412_SALE_FAB_QTY, 0) AS M202412_SALE_FAB_QTY
                                                                   , NVL(M202412_SALE_EQ_QTY, 0)  AS M202412_SALE_EQ_QTY
                                                                   , NVL(M202412_SALE_ASP, 0)     AS M202412_SALE_ASP
                                                                   , NVL(M202412_SALE_PKG_ASP, 0) AS M202412_SALE_PKG_ASP
                                                                   , NVL(M202412_SALE_FAB_ASP, 0) AS M202412_SALE_FAB_ASP
                                                                   , NVL(M202412_SALE_EQ_ASP, 0)  AS M202412_SALE_EQ_ASP
                                                                   , NVL(M202412_SALE_AMT, 0)     AS M202412_SALE_AMT
                                                                   , NVL(M202412_INV_QTY, 0)      AS M202412_INV_QTY
                                                                   , NVL(M202412_INV_PKG_QTY, 0)  AS M202412_INV_PKG_QTY
                                                                   , NVL(M202412_INV_FAB_QTY, 0)  AS M202412_INV_FAB_QTY
                                                                   , NVL(M202412_INV_EQ_QTY, 0)   AS M202412_INV_EQ_QTY
                                                                   , NVL(M202501_SALE_QTY, 0)     AS M202501_SALE_QTY
                                                                   , NVL(M202501_SALE_PKG_QTY, 0) AS M202501_SALE_PKG_QTY
                                                                   , NVL(M202501_SALE_FAB_QTY, 0) AS M202501_SALE_FAB_QTY
                                                                   , NVL(M202501_SALE_EQ_QTY, 0)  AS M202501_SALE_EQ_QTY
                                                                   , NVL(M202501_SALE_ASP, 0)     AS M202501_SALE_ASP
                                                                   , NVL(M202501_SALE_PKG_ASP, 0) AS M202501_SALE_PKG_ASP
                                                                   , NVL(M202501_SALE_FAB_ASP, 0) AS M202501_SALE_FAB_ASP
                                                                   , NVL(M202501_SALE_EQ_ASP, 0)  AS M202501_SALE_EQ_ASP
                                                                   , NVL(M202501_SALE_AMT, 0)     AS M202501_SALE_AMT
                                                                   , NVL(M202501_INV_QTY, 0)      AS M202501_INV_QTY
                                                                   , NVL(M202501_INV_PKG_QTY, 0)  AS M202501_INV_PKG_QTY
                                                                   , NVL(M202501_INV_FAB_QTY, 0)  AS M202501_INV_FAB_QTY
                                                                   , NVL(M202501_INV_EQ_QTY, 0)   AS M202501_INV_EQ_QTY
                                                                   , NVL(M202502_SALE_QTY, 0)     AS M202502_SALE_QTY
                                                                   , NVL(M202502_SALE_PKG_QTY, 0) AS M202502_SALE_PKG_QTY
                                                                   , NVL(M202502_SALE_FAB_QTY, 0) AS M202502_SALE_FAB_QTY
                                                                   , NVL(M202502_SALE_EQ_QTY, 0)  AS M202502_SALE_EQ_QTY
                                                                   , NVL(M202502_SALE_ASP, 0)     AS M202502_SALE_ASP
                                                                   , NVL(M202502_SALE_PKG_ASP, 0) AS M202502_SALE_PKG_ASP
                                                                   , NVL(M202502_SALE_FAB_ASP, 0) AS M202502_SALE_FAB_ASP
                                                                   , NVL(M202502_SALE_EQ_ASP, 0)  AS M202502_SALE_EQ_ASP
                                                                   , NVL(M202502_SALE_AMT, 0)     AS M202502_SALE_AMT
                                                                   , NVL(M202502_INV_QTY, 0)      AS M202502_INV_QTY
                                                                   , NVL(M202502_INV_PKG_QTY, 0)  AS M202502_INV_PKG_QTY
                                                                   , NVL(M202502_INV_FAB_QTY, 0)  AS M202502_INV_FAB_QTY
                                                                   , NVL(M202502_INV_EQ_QTY, 0)   AS M202502_INV_EQ_QTY
                                                                   , NVL(M202503_SALE_QTY, 0)     AS M202503_SALE_QTY
                                                                   , NVL(M202503_SALE_PKG_QTY, 0) AS M202503_SALE_PKG_QTY
                                                                   , NVL(M202503_SALE_FAB_QTY, 0) AS M202503_SALE_FAB_QTY
                                                                   , NVL(M202503_SALE_EQ_QTY, 0)  AS M202503_SALE_EQ_QTY
                                                                   , NVL(M202503_SALE_ASP, 0)     AS M202503_SALE_ASP
                                                                   , NVL(M202503_SALE_PKG_ASP, 0) AS M202503_SALE_PKG_ASP
                                                                   , NVL(M202503_SALE_FAB_ASP, 0) AS M202503_SALE_FAB_ASP
                                                                   , NVL(M202503_SALE_EQ_ASP, 0)  AS M202503_SALE_EQ_ASP
                                                                   , NVL(M202503_SALE_AMT, 0)     AS M202503_SALE_AMT
                                                                   , NVL(M202503_INV_QTY, 0)      AS M202503_INV_QTY
                                                                   , NVL(M202503_INV_PKG_QTY, 0)  AS M202503_INV_PKG_QTY
                                                                   , NVL(M202503_INV_FAB_QTY, 0)  AS M202503_INV_FAB_QTY
                                                                   , NVL(M202503_INV_EQ_QTY, 0)   AS M202503_INV_EQ_QTY
                                                                   , NVL(M202504_SALE_QTY, 0)     AS M202504_SALE_QTY
                                                                   , NVL(M202504_SALE_PKG_QTY, 0) AS M202504_SALE_PKG_QTY
                                                                   , NVL(M202504_SALE_FAB_QTY, 0) AS M202504_SALE_FAB_QTY
                                                                   , NVL(M202504_SALE_EQ_QTY, 0)  AS M202504_SALE_EQ_QTY
                                                                   , NVL(M202504_SALE_ASP, 0)     AS M202504_SALE_ASP
                                                                   , NVL(M202504_SALE_PKG_ASP, 0) AS M202504_SALE_PKG_ASP
                                                                   , NVL(M202504_SALE_FAB_ASP, 0) AS M202504_SALE_FAB_ASP
                                                                   , NVL(M202504_SALE_EQ_ASP, 0)  AS M202504_SALE_EQ_ASP
                                                                   , NVL(M202504_SALE_AMT, 0)     AS M202504_SALE_AMT
                                                                   , NVL(M202504_INV_QTY, 0)      AS M202504_INV_QTY
                                                                   , NVL(M202504_INV_PKG_QTY, 0)  AS M202504_INV_PKG_QTY
                                                                   , NVL(M202504_INV_FAB_QTY, 0)  AS M202504_INV_FAB_QTY
                                                                   , NVL(M202504_INV_EQ_QTY, 0)   AS M202504_INV_EQ_QTY
                                                                FROM(
                                                                            SELECT SCM_FAMILY_CD
                                                                                 , TECH_CD
                                                                                 , FAB_DEN_CD
                                                                                 , CHG_PROD_MODE_CD
                                                                                 , CELL_LAYER_TYP_CD
                                                                                 , PLN_REV
                                                                                 , TGT_YM
                                                                                 , SALE_QTY
                                                                                 , SALE_PKG_QTY
                                                                                 , SALE_FAB_QTY
                                                                                 , SALE_EQ_QTY
                                                                                 , SALE_ASP
                                                                                 , SALE_PKG_ASP
                                                                                 , SALE_FAB_ASP
                                                                                 , SALE_EQ_ASP
                                                                                 , SALE_AMT
                                                                                 , INV_QTY
                                                                                 , INV_PKG_QTY
                                                                                 , INV_FAB_QTY
                                                                                 , INV_EQ_QTY
                                                                              FROM ORG_SOURCE_WITH
                                                                     )
                                                                     PIVOT(SUM(SALE_QTY) AS SALE_QTY, SUM(SALE_PKG_QTY) AS SALE_PKG_QTY, SUM(SALE_FAB_QTY) AS SALE_FAB_QTY, SUM(SALE_EQ_QTY) AS SALE_EQ_QTY, SUM(SALE_ASP) AS SALE_ASP, SUM(SALE_PKG_ASP) AS SALE_PKG_ASP, SUM(SALE_FAB_ASP) AS SALE_FAB_ASP, SUM(SALE_EQ_ASP) AS SALE_EQ_ASP, SUM(SALE_AMT) AS SALE_AMT, SUM(INV_QTY) AS INV_QTY, SUM(INV_PKG_QTY) AS INV_PKG_QTY, SUM(INV_FAB_QTY) AS INV_FAB_QTY, SUM(INV_EQ_QTY) AS INV_EQ_QTY FOR TGT_YM IN('202401' AS M202401
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
                                                                                                                                                                                                        , '202501' AS M202501
                                                                                                                                                                                                        , '202502' AS M202502
                                                                                                                                                                                                        , '202503' AS M202503
                                                                                                                                                                                                        , '202504' AS M202504))
                                                       )
                                         )
                           )
                  GROUP BY ROLLUP(SCM_FAMILY_CD, TECH_CD, FAB_DEN_CD, CHG_PROD_MODE_CD, CELL_LAYER_TYP_CD
                           /* ,PLN_REV */
                           )
         )
         T1
ORDER BY TO_NUMBER(FAMILY_CD_SEQ)
       , SCM_FAMILY_CD
       , TO_NUMBER(TECH_CD_SEQ)
       , TECH_CD
       , TO_NUMBER(FAB_DEN_CD_SEQ)
       , FAB_DEN_CD
       , TO_NUMBER(CHG_PROD_MODE_CD_SEQ)
       , CHG_PROD_MODE_CD
       , TO_NUMBER(CELL_LAYER_TYP_CD_SEQ)
       , CELL_LAYER_TYP_CD
       , GROUPING_CNT