-- #########################################################################################################
--  1. 가중평균 수율계산
--  개발DB 연결시 PKG정보가 ON_YLD_RLS_GRP 테이블에 통합되어 아래 쿼리 '@@@@@@@@@@' 영역 주석처리
--  수율(YLD), 생산량(OUT_QTY)
-- #########################################################################################################
WITH DEVICE_LIST AS
(
		 SELECT
				 	  RLS_YM, RLS_YW, RLS_TYP_CD, DATA_GBN_CD, WORK_YW
		      , FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, PROD_MODE_CD, CELL_LAYER_TYP_CD_ADJUST, SCM_PROD_VER_CD
          , DEVICE_CD_ADJUST, LINE_GRP_CD, DECODE(LINE_GRP_CD, 'WFT', 1,3) AS LINE_SEQ
          , YLD, PLN_YLD
		      , OUT_QTY, EQ_OUT_QTY, NORM_OUT_QTY, NORM_EQ_OUT_QTY
				  , FAMILY_CD ||' ' || FAB_ID ||' ' ||
            TECH_CD ||' ' || FAB_DEN_CD
		        ||' ' || PROD_MODE_CD ||' ' || CELL_LAYER_TYP_CD_ADJUST
		        ||' ' || SCM_PROD_VER_CD AS DEVICE_GRP_KEY
          , TECH_CD ||' ' || FAB_DEN_CD
		        ||' ' || PROD_MODE_CD ||' ' || CELL_LAYER_TYP_CD_ADJUST
		        ||' ' || SCM_PROD_VER_CD AS DEVICE_GRP_KEY2
		   FROM ON_YLD_RLS_GRP				/* ■ WT, PKT */
		  WHERE RLS_YW 			= '202306'
				AND RLS_TYP_CD 	= 'Y0205_01_ALL'
		    AND WORK_YW 		= '202306'
				AND DATA_GBN_CD IN ('MFG_ACT_WW', 'MFG_PLN_WW', 'YLD_ACT_WW', 'YLD_PLN_WW')

     /* @@@@@@@@@@ */
		 UNION ALL

		 SELECT
			 		  RLS_YM, RLS_YW, RLS_TYP_CD, DATA_GBN_CD, WORK_YW
		      , FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, PROD_MODE_CD, CELL_LAYER_TYP_CD_ADJUST, SCM_PROD_VER_CD
          , DEVICE_CD_ADJUST, LINE_GRP_CD, 2 AS LINE_SEQ
          , YLD, PLN_YLD
		      , OUT_QTY, EQ_OUT_QTY, NORM_OUT_QTY, NORM_EQ_OUT_QTY
				  , FAMILY_CD ||' ' || FAB_ID ||' ' ||
            TECH_CD ||' ' || FAB_DEN_CD
		        ||' ' || PROD_MODE_CD ||' ' || CELL_LAYER_TYP_CD_ADJUST
		        ||' ' || SCM_PROD_VER_CD AS DEVICE_GRP_KEY
          , TECH_CD ||' ' || FAB_DEN_CD
		        ||' ' || PROD_MODE_CD ||' ' || CELL_LAYER_TYP_CD_ADJUST
		        ||' ' || SCM_PROD_VER_CD AS DEVICE_GRP_KEY2
		   FROM ON_YLD_RLS_GRP_CUM   	/* ■ PKG */
		  WHERE 1 = 1
		    AND RLS_YW 			= '202306'
				AND RLS_TYP_CD 	= 'Y0205_01_ALL'
		    AND WORK_YW 		= '202306'
				AND DATA_GBN_CD IN ('MFG_ACT_WW', 'MFG_PLN_WW', 'YLD_ACT_WW', 'YLD_PLN_WW')
     /* @@@@@@@@@@ */
)
, DEVICE_LIST_CAL AS
(
		 SELECT RLS_YM, RLS_YW, RLS_TYP_CD, WORK_YW
		      , FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, PROD_MODE_CD, CELL_LAYER_TYP_CD_ADJUST, SCM_PROD_VER_CD
          , DEVICE_CD_ADJUST, LINE_GRP_CD
		      , DEVICE_GRP_KEY, LINE_SEQ, DEVICE_GRP_KEY2
		      , CAL_YLD																																																			/* 수율-계획 */
					, CAL_YLD_ACT																																																	/* 수율-실적 */
					, CAL_MFG																																																			/* 수량-계획 */
					, CAL_MFG_ACT																																																	/* 수량-실적 */
				  , CAL_MFG_TOT																																																	/* 합계-계획 */
				  , CAL_MFG_ACT_TOT																																															/* 합계-실적 */
          , NVL(CAL_MFG / DECODE(CAL_MFG_TOT, 0, NULL, CAL_MFG_TOT)*100, 0) AS CAL_MFG_RTO															/* 비중-계획 */
          , NVL(CAL_MFG_ACT / DECODE(CAL_MFG_ACT_TOT, 0, NULL, CAL_MFG_ACT_TOT)*100, 0) AS CAL_MFG_ACT_RTO							/* 비중-실적 */
          , CAL_YLD * NVL(CAL_MFG / DECODE(CAL_MFG_TOT, 0, NULL, CAL_MFG_TOT), 0) AS CAL_WGT_YLD												/* 가중-계획 */
					, CAL_YLD_ACT * NVL(CAL_MFG_ACT / DECODE(CAL_MFG_ACT_TOT, 0, NULL, CAL_MFG_ACT_TOT), 0) AS CAL_WGT_YLD_ACT		/* 가중-실적 */
      FROM (
				     SELECT RLS_YM, RLS_YW, RLS_TYP_CD, WORK_YW
						      , FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, PROD_MODE_CD, CELL_LAYER_TYP_CD_ADJUST, SCM_PROD_VER_CD
                  , DEVICE_CD_ADJUST, LINE_GRP_CD, DEVICE_GRP_KEY2
						      , DEVICE_GRP_KEY, LINE_SEQ
						      , CAL_YLD
						      , CAL_YLD_ACT
						      , CAL_MFG
						      , CAL_MFG_ACT
				     			, SUM(CAL_MFG) OVER (PARTITION BY DEVICE_GRP_KEY, LINE_GRP_CD) AS CAL_MFG_TOT
				     			, SUM(CAL_MFG_ACT) OVER (PARTITION BY DEVICE_GRP_KEY, LINE_GRP_CD) AS CAL_MFG_ACT_TOT
				       FROM (
											SELECT RLS_YM, RLS_YW, RLS_TYP_CD, WORK_YW
											     , FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, PROD_MODE_CD, CELL_LAYER_TYP_CD_ADJUST, SCM_PROD_VER_CD
                           , DEVICE_CD_ADJUST, LINE_GRP_CD, DEVICE_GRP_KEY2
											     , DEVICE_GRP_KEY, LINE_SEQ
											     , SUM(CASE WHEN DATA_GBN_CD = 'YLD_PLN_WW' THEN YLD ELSE 0 END) AS CAL_YLD
											     , SUM(CASE WHEN DATA_GBN_CD = 'YLD_ACT_WW' THEN YLD ELSE 0 END) AS CAL_YLD_ACT
											     , SUM(CASE WHEN DATA_GBN_CD = 'MFG_PLN_WW' THEN OUT_QTY ELSE 0 END) AS CAL_MFG
											     , SUM(CASE WHEN DATA_GBN_CD = 'MFG_ACT_WW' THEN OUT_QTY ELSE 0 END) AS CAL_MFG_ACT
											  FROM DEVICE_LIST
											 WHERE 1 = 1
                       	 /* ◆ 특정 DEVICE 조회 ◆ */
											 	 --AND FAMILY_CD = 'DRAM' AND FAB_ID = 'C2' AND TECH_CD = 'DA' AND FAB_DEN_CD = '8G' AND PROD_MODE_CD = 'LPDDR4'
                         --AND FAMILY_CD = 'NAND' AND FAB_ID = 'M15' AND TECH_CD = 'PE' AND FAB_DEN_CD = '512G' AND PROD_MODE_CD = 'Raw NAND'

											 GROUP BY RLS_YM, RLS_YW, RLS_TYP_CD, WORK_YW
											     , FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, PROD_MODE_CD, CELL_LAYER_TYP_CD_ADJUST, SCM_PROD_VER_CD
                           , DEVICE_CD_ADJUST, LINE_GRP_CD, DEVICE_GRP_KEY2
											     , DEVICE_GRP_KEY, LINE_SEQ
				            )
				      GROUP BY RLS_YM, RLS_YW, RLS_TYP_CD, WORK_YW
										 , FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, PROD_MODE_CD, CELL_LAYER_TYP_CD_ADJUST, SCM_PROD_VER_CD
                     , DEVICE_CD_ADJUST, LINE_GRP_CD
										 , DEVICE_GRP_KEY, LINE_SEQ, DEVICE_GRP_KEY2
				             , CAL_YLD, CAL_YLD_ACT, CAL_MFG, CAL_MFG_ACT
           )
)
, DEVICE_GRP_LIST_CAL AS
(
					SELECT RLS_YM, RLS_YW, RLS_TYP_CD, WORK_YW
					     , FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, PROD_MODE_CD, CELL_LAYER_TYP_CD_ADJUST, SCM_PROD_VER_CD
               , DEVICE_GRP_KEY2 AS DEVICE_CD_ADJUST, LINE_GRP_CD
					     , DEVICE_GRP_KEY, LINE_SEQ, DEVICE_GRP_KEY2
					     , SUM(CAL_WGT_YLD) AS CAL_YLD, 	SUM(CAL_WGT_YLD_ACT) AS CAL_YLD_ACT
							 , NULL AS CAL_MFG, 		NULL AS CAL_MFG_ACT
							 , NULL AS CAL_MFG_TOT, NULL AS CAL_MFG_ACT_TOT
			         , NULL AS CAL_MFG_RTO, NULL AS CAL_MFG_ACT_RTO
			         , NULL AS CAL_WGT_YLD, NULL AS CAL_WGT_YLD_ACT
          		 , 2 AS CUM_SORT
					  FROM DEVICE_LIST_CAL B
           WHERE 1 = 1
           GROUP BY RLS_YM, RLS_YW, RLS_TYP_CD, WORK_YW
					     , FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, PROD_MODE_CD, CELL_LAYER_TYP_CD_ADJUST, SCM_PROD_VER_CD
					     , DEVICE_GRP_KEY, LINE_GRP_CD, LINE_SEQ, DEVICE_GRP_KEY2
)

SELECT '가중평균 검증' AS TITLE
     --, RLS_YM, RLS_YW, RLS_TYP_CD, WORK_YW
	   , FAMILY_CD, FAB_ID --, TECH_CD, FAB_DEN_CD, PROD_MODE_CD, CELL_LAYER_TYP_CD_ADJUST, SCM_PROD_VER_CD
	   , DEVICE_CD_ADJUST, LINE_GRP_CD
	   --, DEVICE_GRP_KEY, LINE_SEQ
     , CAL_YLD, 		CAL_YLD_ACT						/* 수율 */
		 , CAL_MFG, 		CAL_MFG_ACT						/* 수량 */
		 --, CAL_MFG_TOT, CAL_MFG_ACT_TOT				/* 합계 */
	   , CAL_MFG_RTO, CAL_MFG_ACT_RTO				/* 비중 */
	   , CAL_WGT_YLD, CAL_WGT_YLD_ACT				/* 가중 */
     , CUM_SORT
  FROM (
  				/* 1-DEVICE LIST */
					SELECT RLS_YM, RLS_YW, RLS_TYP_CD, WORK_YW
					     , FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, PROD_MODE_CD, CELL_LAYER_TYP_CD_ADJUST, SCM_PROD_VER_CD
               , DEVICE_CD_ADJUST, LINE_GRP_CD
					     , DEVICE_GRP_KEY, LINE_SEQ
					     , CAL_YLD, 		CAL_YLD_ACT
							 , CAL_MFG, 		CAL_MFG_ACT
							 , CAL_MFG_TOT, CAL_MFG_ACT_TOT
			         , CAL_MFG_RTO, CAL_MFG_ACT_RTO
			         , CAL_WGT_YLD, CAL_WGT_YLD_ACT
               , 1 AS CUM_SORT
					  FROM DEVICE_LIST_CAL A

          UNION ALL

					/* 2-LINE BY TOT LIST */
          SELECT RLS_YM, RLS_YW, RLS_TYP_CD, WORK_YW
					     , FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, PROD_MODE_CD, CELL_LAYER_TYP_CD_ADJUST, SCM_PROD_VER_CD
               , DEVICE_CD_ADJUST, LINE_GRP_CD
					     , DEVICE_GRP_KEY, LINE_SEQ
					     , CAL_YLD, 		CAL_YLD_ACT
							 , CAL_MFG, 		CAL_MFG_ACT
							 , CAL_MFG_TOT, CAL_MFG_ACT_TOT
			         , CAL_MFG_RTO, CAL_MFG_ACT_RTO
			         , CAL_WGT_YLD, CAL_WGT_YLD_ACT
               , 2 AS CUM_SORT
					  FROM DEVICE_GRP_LIST_CAL B

          UNION ALL

          /* 3-CUM1 LIST */
          SELECT RLS_YM, RLS_YW, RLS_TYP_CD, WORK_YW
					     , FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, PROD_MODE_CD, CELL_LAYER_TYP_CD_ADJUST, SCM_PROD_VER_CD
               , DEVICE_GRP_KEY2 AS DEVICE_CD_ADJUST, 'CUM1' AS LINE_GRP_CD
					     , DEVICE_GRP_KEY, 4 AS LINE_SEQ
               , ROUND(EXP(SUM(LN(DECODE(NVL(CAL_YLD, 0), 0, 1, CAL_YLD)))) / ROUND(EXP(SUM(LN(DECODE(NVL(CAL_YLD,0), 0, 1, 100)))),0) * 100, 9) AS CAL_YLD
               , ROUND(EXP(SUM(LN(DECODE(NVL(CAL_YLD_ACT, 0), 0, 1, CAL_YLD_ACT)))) / ROUND(EXP(SUM(LN(DECODE(NVL(CAL_YLD_ACT,0), 0, 1, 100)))),0) * 100, 9)  AS CAL_YLD_ACT
               , NULL AS CAL_MFG, 		NULL AS CAL_MFG_ACT
							 , NULL AS CAL_MFG_TOT, NULL AS CAL_MFG_ACT_TOT
			         , NULL AS CAL_MFG_RTO, NULL AS CAL_MFG_ACT_RTO
			         , NULL AS CAL_WGT_YLD, NULL AS CAL_WGT_YLD_ACT
          		 , 3 AS CUM_SORT
					  FROM DEVICE_GRP_LIST_CAL C
          GROUP BY RLS_YM, RLS_YW, RLS_TYP_CD, WORK_YW
					     , FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, PROD_MODE_CD, CELL_LAYER_TYP_CD_ADJUST, SCM_PROD_VER_CD
					     , DEVICE_GRP_KEY, DEVICE_GRP_KEY2
       )
 WHERE 1 = 1
   --AND FAMILY_CD = 'DRAM' AND FAB_ID = 'C2' AND TECH_CD = 'DA' AND FAB_DEN_CD = '8G' AND PROD_MODE_CD = 'LPDDR4'
 ORDER BY FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, PROD_MODE_CD, SCM_PROD_VER_CD, CUM_SORT, LINE_SEQ
;
-- #########################################################################################################
