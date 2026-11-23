/*------------------------------------------------------------------------------
-- 개체 이름: RPLS_ADM.RPI_SOM_MG_VW_TEST_MKH
-- 만든 날짜: 2018-09-07 오전 9:41:30
-- 마지막 수정 날짜: 2022-11-22 오후 6:04:07
-- 상태: VALID
------------------------------------------------------------------------------*/
CREATE OR REPLACE FORCE VIEW RPLS_ADM.RPI_SOM_MG_VW_TEST_MKH
( PLN_REV, RP_SOM_CD, CUST_ID, APP_LVL_1_CD,
  REGION_ID, TGT_YM, PLN_YM, PLN_WEEK_GBN_CD,
  GA_GBN_CD, CS_DT, SOM_SUM_QTY, SOM_STRGY_QTY,
  SOM_GNRAL_QTY, SOM_AVL_QTY, SOM_AVL_STRGY_QTY, SOM_AVL_GNRAL_QTY,
  SOM_RMA_QTY, SOM_SUM_AMT, SOM_STRGY_AMT, SOM_GNRAL_AMT,
  SOM_AVL_AMT, SOM_AVL_STRGY_AMT, SOM_AVL_GNRAL_AMT, SOM_RMA_AMT,
  SHIFT_APPLY_YN, PRE_LOOK_SHIFT_APPLY_YN, PRE_LOOK_SOM_SUM_QTY, CRT_TM,
  CRT_USER_ID, CHG_TM, CHG_USER_ID, ORG_SCM_FAMILY_CD,
  ORG_SCM_FAMILY_CD2, SCM_FAMILY_CD, ORG_RP_SOM_CD )
AS
SELECT	A.PLN_REV,
    	A.RP_SOM_CD,
	    A.CUST_ID,
	    A.APP_LVL_1_CD,
	    A.REGION_ID,
	    A.TGT_YM,
	    A.PLN_YM,
	    A.PLN_WEEK_GBN_CD,
	    A.GA_GBN_CD,
        A.CS_DT,
	    A.SOM_SUM_QTY,
	    A.SOM_STRGY_QTY,
	    A.SOM_GNRAL_QTY,
	    A.SOM_AVL_QTY,
	    A.SOM_AVL_STRGY_QTY,
	    A.SOM_AVL_GNRAL_QTY,
	    A.SOM_RMA_QTY,
	    A.SOM_SUM_AMT,
	    A.SOM_STRGY_AMT,
	    A.SOM_GNRAL_AMT,
	    A.SOM_AVL_AMT,
	    A.SOM_AVL_STRGY_AMT,
	    A.SOM_AVL_GNRAL_AMT,
	    A.SOM_RMA_AMT,
	    A.SHIFT_APPLY_YN,
  	    A.PRE_LOOK_SHIFT_APPLY_YN,
        A.PRE_LOOK_SOM_SUM_QTY,
	    A.CRT_TM,
	    A.CRT_USER_ID,
	    A.CHG_TM,
	    A.CHG_USER_ID,
	    B.SCM_FAMILY_CD AS ORG_SCM_FAMILY_CD,
        B.SCM_FAMILY_CD AS ORG_SCM_FAMILY_CD2,
        B.SCM_FAMILY_CD AS SCM_FAMILY_CD,
	    A.RP_SOM_CD AS ORG_RP_SOM_CD
  FROM	RPI_SOM A,
  		RPI_RP_SOM_CD_VW B
 WHERE	A.RP_SOM_CD = B.RP_SOM_CD
   --AND	A.RP_SOM_CD LIKE '%HBM%' -- 2021.11.30
   --AND A.RP_SOM_CD IN ('DA_0G_HBM3_1ST_TSV 12DP_C','DA_0G_HBM3_1ST_TSV ODP_C','DA_16G_HBM2E_1ST_TSV ODP_C','DA_16G_HBM2E_1ST_TSV QDP_C','DE_8G_HBM2_2ND_TSV ODP_C','DE_8G_HBM2_2ND_TSV QDP_C') -- 2021.11.30
   AND A.RP_SOM_CD IN (SELECT DISTINCT RP_SOM_CD FROM STI_RPCODE_M WHERE RP_SOM_CD LIKE '%HBM%' AND RP_SOM_CD NOT IN ('DA_16G_HBM3_1ST_TSV ODP_C','DA_16G_HBM3_1ST_TSV 12DP_C'))
UNION ALL
SELECT	A.PLN_REV,
        B.SUB_RP_SOM_CD AS RP_SOM_CD,
        A.CUST_ID,
        A.APP_LVL_1_CD,
        A.REGION_ID,
        A.TGT_YM,
        A.PLN_YM,
        A.PLN_WEEK_GBN_CD,
        A.GA_GBN_CD,
        A.CS_DT,
        SOM_SUM_QTY   * B.SUB_RP_SOM_CNT AS SOM_SUM_QTY,
        SOM_STRGY_QTY * B.SUB_RP_SOM_CNT AS SOM_STRGY_QTY,
        SOM_GNRAL_QTY * B.SUB_RP_SOM_CNT AS SOM_GNRAL_QTY,
        SOM_AVL_QTY   * B.SUB_RP_SOM_CNT AS SOM_AVL_QTY,
        SOM_AVL_STRGY_QTY * B.SUB_RP_SOM_CNT AS SOM_AVL_STRGY_QTY,
        SOM_AVL_GNRAL_QTY * B.SUB_RP_SOM_CNT AS SOM_AVL_GNRAL_QTY,
        SOM_RMA_QTY * B.SUB_RP_SOM_CNT AS SOM_RMA_QTY,

        CASE --WHEN B.SCM_FAMILY_CD = 'DRAM' AND (SUB_RP_SOM_CD LIKE '%#_BASE%' ESCAPE '#' OR SUB_RP_SOM_CD LIKE '%BASE#_%' ESCAPE '#') AND DRAM_LOOSE_ALL_QTY > 1 THEN 0
        	 --WHEN B.SCM_FAMILY_CD = 'DRAM'			THEN D_SOM_SUM_AMT / DRAM_LOOSE_QTY
             WHEN B.SCM_FAMILY_CD     = 'DRAM' THEN D_SOM_SUM_AMT * (DRAM_LOOSE_QTY/DRAM_LOOSE_ALL_QTY) -- 2021.11.30
        	 WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' THEN D_SOM_SUM_AMT / MCPSSD_DRAM_LOOSE_QTY
             WHEN B.SUB_SCM_FAMILY_CD = 'NAND' THEN F_SOM_SUM_AMT / MCPSSD_FLASH_LOOSE_QTY
             ELSE 0
        END AS SOM_SUM_AMT,
        CASE --WHEN B.SCM_FAMILY_CD = 'DRAM' AND (SUB_RP_SOM_CD LIKE '%#_BASE%' ESCAPE '#' OR SUB_RP_SOM_CD LIKE '%BASE#_%' ESCAPE '#') AND DRAM_LOOSE_ALL_QTY > 1 THEN 0
        	 --WHEN B.SCM_FAMILY_CD = 'DRAM'			THEN D_SOM_STRGY_AMT / DRAM_LOOSE_QTY
             WHEN B.SCM_FAMILY_CD     = 'DRAM' THEN D_SOM_STRGY_AMT * (DRAM_LOOSE_QTY/DRAM_LOOSE_ALL_QTY) -- 2021.11.30
             WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' THEN D_SOM_STRGY_AMT / MCPSSD_DRAM_LOOSE_QTY
             WHEN B.SUB_SCM_FAMILY_CD = 'NAND' THEN F_SOM_STRGY_AMT / MCPSSD_FLASH_LOOSE_QTY
             ELSE 0
        END AS SOM_STRGY_AMT,
        CASE --WHEN B.SCM_FAMILY_CD = 'DRAM' AND (SUB_RP_SOM_CD LIKE '%#_BASE%' ESCAPE '#' OR SUB_RP_SOM_CD LIKE '%BASE#_%' ESCAPE '#') AND DRAM_LOOSE_ALL_QTY > 1 THEN 0
        	 --WHEN B.SCM_FAMILY_CD = 'DRAM'			THEN D_SOM_GNRAL_AMT / DRAM_LOOSE_QTY
             WHEN B.SCM_FAMILY_CD     = 'DRAM' THEN D_SOM_GNRAL_AMT * (DRAM_LOOSE_QTY/DRAM_LOOSE_ALL_QTY) -- 2021.11.30
        	 WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' THEN D_SOM_GNRAL_AMT / MCPSSD_DRAM_LOOSE_QTY
             WHEN B.SUB_SCM_FAMILY_CD = 'NAND' THEN F_SOM_GNRAL_AMT / MCPSSD_FLASH_LOOSE_QTY
             ELSE 0
        END AS SOM_GNRAL_AMT,
        CASE --WHEN B.SCM_FAMILY_CD = 'DRAM' AND (SUB_RP_SOM_CD LIKE '%#_BASE%' ESCAPE '#' OR SUB_RP_SOM_CD LIKE '%BASE#_%' ESCAPE '#') AND DRAM_LOOSE_ALL_QTY > 1 THEN 0
        	 --WHEN B.SCM_FAMILY_CD     = 'DRAM' THEN D_SOM_AVL_AMT / DRAM_LOOSE_QTY
             WHEN B.SCM_FAMILY_CD     = 'DRAM' THEN D_SOM_AVL_AMT * (DRAM_LOOSE_QTY/DRAM_LOOSE_ALL_QTY) -- 2021.11.30
        	 WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' THEN D_SOM_AVL_AMT / MCPSSD_DRAM_LOOSE_QTY
             WHEN B.SUB_SCM_FAMILY_CD = 'NAND' THEN F_SOM_AVL_AMT / MCPSSD_FLASH_LOOSE_QTY
             ELSE 0
        END AS SOM_AVL_AMT,
        CASE --WHEN B.SCM_FAMILY_CD = 'DRAM' AND (SUB_RP_SOM_CD LIKE '%#_BASE%' ESCAPE '#' OR SUB_RP_SOM_CD LIKE '%BASE#_%' ESCAPE '#') AND DRAM_LOOSE_ALL_QTY > 1 THEN 0
        	 --WHEN B.SCM_FAMILY_CD     = 'DRAM' THEN D_SOM_AVL_STRGY_AMT / DRAM_LOOSE_QTY
             WHEN B.SCM_FAMILY_CD     = 'DRAM' THEN D_SOM_AVL_STRGY_AMT * (DRAM_LOOSE_QTY/DRAM_LOOSE_ALL_QTY) -- 2021.11.30
             WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' THEN D_SOM_AVL_STRGY_AMT / MCPSSD_DRAM_LOOSE_QTY
             WHEN B.SUB_SCM_FAMILY_CD = 'NAND' THEN F_SOM_AVL_STRGY_AMT / MCPSSD_FLASH_LOOSE_QTY
             ELSE 0
        END AS SOM_AVL_STRGY_AMT,
        CASE --WHEN B.SCM_FAMILY_CD = 'DRAM' AND (SUB_RP_SOM_CD LIKE '%#_BASE%' ESCAPE '#' OR SUB_RP_SOM_CD LIKE '%BASE#_%' ESCAPE '#') AND DRAM_LOOSE_ALL_QTY > 1 THEN 0
        	 --WHEN B.SCM_FAMILY_CD     = 'DRAM' THEN D_SOM_AVL_GNRAL_AMT / DRAM_LOOSE_QTY
             WHEN B.SCM_FAMILY_CD     = 'DRAM' THEN D_SOM_AVL_GNRAL_AMT * (DRAM_LOOSE_QTY/DRAM_LOOSE_ALL_QTY) -- 2021.11.30
        	 WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' THEN D_SOM_AVL_GNRAL_AMT / MCPSSD_DRAM_LOOSE_QTY
             WHEN B.SUB_SCM_FAMILY_CD = 'NAND' THEN F_SOM_AVL_GNRAL_AMT / MCPSSD_FLASH_LOOSE_QTY
             ELSE 0
        END AS SOM_AVL_GNRAL_AMT,
        CASE --WHEN B.SCM_FAMILY_CD = 'DRAM' AND (SUB_RP_SOM_CD LIKE '%#_BASE%' ESCAPE '#' OR SUB_RP_SOM_CD LIKE '%BASE#_%' ESCAPE '#') AND DRAM_LOOSE_ALL_QTY > 1 THEN 0
        	 --WHEN B.SCM_FAMILY_CD     = 'DRAM' THEN D_SOM_RMA_AMT / DRAM_LOOSE_QTY
             WHEN B.SCM_FAMILY_CD     = 'DRAM' THEN D_SOM_RMA_AMT * (DRAM_LOOSE_QTY/DRAM_LOOSE_ALL_QTY) -- 2021.11.30
        	 WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' THEN D_SOM_RMA_AMT / MCPSSD_DRAM_LOOSE_QTY
             WHEN B.SUB_SCM_FAMILY_CD = 'NAND' THEN F_SOM_RMA_AMT / MCPSSD_FLASH_LOOSE_QTY
             ELSE 0
        END AS SOM_RMA_AMT,
	    A.SHIFT_APPLY_YN,
  	    A.PRE_LOOK_SHIFT_APPLY_YN,
        PRE_LOOK_SOM_SUM_QTY * B.SUB_RP_SOM_CNT AS PRE_LOOK_SOM_SUM_QTY,
        CRT_TM,
        CRT_USER_ID,
        CHG_TM,
        CHG_USER_ID,
        B.SCM_FAMILY_CD AS ORG_SCM_FAMILY_CD,
        CASE WHEN A.RP_SOM_CD LIKE '%BGA%' THEN 'BGASSD' ELSE B.SCM_FAMILY_CD END AS ORG_SCM_FAMILY_CD2,  -- 2022.02.21
        B.SUB_SCM_FAMILY_CD AS SCM_FAMILY_CD,
        A.RP_SOM_CD AS ORG_RP_SOM_CD
  FROM	(
	        SELECT	A.PLN_REV,
            		A.RP_SOM_CD,
                    A.CUST_ID,
                    A.APP_LVL_1_CD,
                    A.REGION_ID,
                    A.TGT_YM,
          			A.PLN_YM,
                    A.PLN_WEEK_GBN_CD,
                    A.GA_GBN_CD,
                    A.CS_DT,
                    A.SOM_SUM_QTY,
                    A.SOM_STRGY_QTY,
	                A.SOM_GNRAL_QTY,
                    A.SOM_AVL_QTY,
                    A.SOM_AVL_STRGY_QTY,
	                A.SOM_AVL_GNRAL_QTY,
            		A.SOM_RMA_QTY,
	                CASE WHEN B.SCM_FAMILY_CD = 'DRAM' THEN A.SOM_SUM_AMT
	                     WHEN B.SCM_FAMILY_CD = 'Hybrid' THEN CASE WHEN C.RP_SOM_CD IS NULL THEN A.SOM_SUM_AMT
	                            						      ELSE A.SOM_SUM_AMT * C.DRAM_RATE
	                       									  END
	                     WHEN B.SCM_FAMILY_CD = 'SSD' THEN CASE WHEN C.RP_SOM_CD IS NOT NULL AND A.SOM_SUM_AMT > 0
														        THEN A.SOM_SUM_QTY * C.DRAM_PRICE
	                            						   ELSE 0
	                       								   END
	                ELSE 0
	                END D_SOM_SUM_AMT,
	                CASE WHEN B.SCM_FAMILY_CD = 'NAND' THEN A.SOM_SUM_AMT
	                     WHEN B.SCM_FAMILY_CD = 'Hybrid' THEN A.SOM_SUM_AMT - (
                       															CASE WHEN C.RP_SOM_CD IS NULL THEN A.SOM_SUM_AMT
	                                           									ELSE A.SOM_SUM_AMT * C.DRAM_RATE
	                                      										END
                       														  )
	                     WHEN B.SCM_FAMILY_CD = 'SSD' THEN A.SOM_SUM_AMT - (
                      															CASE WHEN C.RP_SOM_CD IS NOT NULL AND A.SOM_SUM_AMT > 0
	                                           										 THEN A.SOM_SUM_QTY * C.DRAM_PRICE
	                                           									ELSE 0
	                                      										END
                      													   )
	                ELSE 0
	                END F_SOM_SUM_AMT,
	                CASE WHEN B.SCM_FAMILY_CD = 'DRAM'  THEN A.SOM_STRGY_AMT
	                     WHEN B.SCM_FAMILY_CD = 'Hybrid' THEN CASE WHEN C.RP_SOM_CD IS NULL THEN A.SOM_STRGY_AMT
	                            							  	   ELSE A.SOM_STRGY_AMT * C.DRAM_RATE
	                       								 	  END
	                     WHEN B.SCM_FAMILY_CD = 'SSD' THEN CASE WHEN C.RP_SOM_CD IS NOT NULL AND A.SOM_STRGY_AMT > 0 THEN A.SOM_STRGY_QTY * C.DRAM_PRICE
	                            						   ELSE 0
	                       								   END
	                ELSE 0
	                END D_SOM_STRGY_AMT,
	                CASE WHEN B.SCM_FAMILY_CD = 'NAND' THEN A.SOM_STRGY_AMT
	                     WHEN B.SCM_FAMILY_CD = 'Hybrid' THEN A.SOM_STRGY_AMT - (
                       															 	CASE WHEN C.RP_SOM_CD IS NULL THEN A.SOM_STRGY_AMT
	                                             									ELSE A.SOM_STRGY_AMT * C.DRAM_RATE
	                                        										END
                       															)
	                     WHEN B.SCM_FAMILY_CD = 'SSD' THEN A.SOM_STRGY_AMT - (
                      														  	CASE WHEN C.RP_SOM_CD IS NOT NULL AND A.SOM_STRGY_AMT > 0
                                                                            		 THEN A.SOM_STRGY_QTY * C.DRAM_PRICE
	                                             								ELSE 0
	                                        									END
                      														 )
	                ELSE 0
	                END F_SOM_STRGY_AMT,
	                CASE WHEN B.SCM_FAMILY_CD = 'DRAM'	THEN A.SOM_GNRAL_AMT
	                     WHEN B.SCM_FAMILY_CD = 'Hybrid' THEN CASE WHEN C.RP_SOM_CD IS NULL THEN A.SOM_GNRAL_AMT
	                            								   ELSE A.SOM_GNRAL_AMT * C.DRAM_RATE
	                       									  END
	                     WHEN B.SCM_FAMILY_CD = 'SSD' THEN CASE WHEN C.RP_SOM_CD IS NOT NULL AND A.SOM_GNRAL_AMT > 0
                       								 		    THEN A.SOM_GNRAL_QTY * C.DRAM_PRICE
	                            						   ELSE 0
	                       								   END
	                     ELSE 0
	                END D_SOM_GNRAL_AMT,
	                CASE WHEN B.SCM_FAMILY_CD = 'NAND' THEN A.SOM_GNRAL_AMT
	                     WHEN B.SCM_FAMILY_CD = 'Hybrid' THEN A.SOM_GNRAL_AMT - (
                       															 	CASE WHEN C.RP_SOM_CD IS NULL THEN A.SOM_GNRAL_AMT
	                                             							 	    ELSE A.SOM_GNRAL_AMT * C.DRAM_RATE
	                                        										END
                       															)
	                     WHEN B.SCM_FAMILY_CD = 'SSD' THEN A.SOM_GNRAL_AMT - (
                       															CASE WHEN C.RP_SOM_CD IS NOT NULL AND A.SOM_GNRAL_AMT > 0
                                                                               		 THEN A.SOM_GNRAL_QTY * C.DRAM_PRICE
	                                             								ELSE 0
	                                        									END
                       														 )
	                     ELSE 0
	                END F_SOM_GNRAL_AMT,
                    CASE WHEN B.SCM_FAMILY_CD = 'DRAM' THEN A.SOM_AVL_AMT
	                     WHEN B.SCM_FAMILY_CD = 'Hybrid' THEN CASE WHEN C.RP_SOM_CD IS NULL THEN A.SOM_AVL_AMT
	                            							  ELSE A.SOM_AVL_AMT * C.DRAM_RATE
	                       									  END
	                     WHEN B.SCM_FAMILY_CD = 'SSD'  THEN CASE WHEN C.RP_SOM_CD IS NOT NULL AND A.SOM_AVL_AMT > 0
													             THEN A.SOM_AVL_QTY * C.DRAM_PRICE
	                            						    ELSE 0
	                       									END
	                ELSE 0
	                END D_SOM_AVL_AMT,
	                CASE WHEN B.SCM_FAMILY_CD = 'NAND' THEN A.SOM_AVL_AMT
	                     WHEN B.SCM_FAMILY_CD = 'Hybrid' THEN A.SOM_AVL_AMT - (
                       														   	CASE WHEN C.RP_SOM_CD IS NULL THEN A.SOM_AVL_AMT
	                                           									ELSE A.SOM_AVL_AMT * C.DRAM_RATE
	                                      										END
                       														  )
	                     WHEN B.SCM_FAMILY_CD = 'SSD' THEN A.SOM_AVL_AMT - (
                      															CASE WHEN C.RP_SOM_CD IS NOT NULL AND A.SOM_AVL_AMT > 0
	                                           										 THEN A.SOM_AVL_QTY * C.DRAM_PRICE
	                                           									ELSE 0
	                                      										END
                      													   )
	                ELSE 0
	                END F_SOM_AVL_AMT,
	                CASE WHEN B.SCM_FAMILY_CD = 'DRAM' THEN A.SOM_AVL_STRGY_AMT
	                     WHEN B.SCM_FAMILY_CD = 'Hybrid' THEN CASE WHEN C.RP_SOM_CD IS NULL THEN A.SOM_AVL_STRGY_AMT
	                            							  ELSE A.SOM_AVL_STRGY_AMT * C.DRAM_RATE
	                       									  END
	                     WHEN B.SCM_FAMILY_CD = 'SSD' THEN CASE WHEN C.RP_SOM_CD IS NOT NULL AND A.SOM_AVL_STRGY_AMT > 0
                         									    THEN A.SOM_AVL_STRGY_QTY * C.DRAM_PRICE
	                            						   ELSE 0
	                       								   END
	                ELSE 0
	                END D_SOM_AVL_STRGY_AMT,
	                CASE WHEN B.SCM_FAMILY_CD = 'NAND' THEN A.SOM_AVL_STRGY_AMT
	                     WHEN B.SCM_FAMILY_CD = 'Hybrid' THEN A.SOM_AVL_STRGY_AMT - (
                       																  	CASE WHEN C.RP_SOM_CD IS NULL THEN A.SOM_AVL_STRGY_AMT
	                                             									    ELSE A.SOM_AVL_STRGY_AMT * C.DRAM_RATE
	                                        											END
                       																)
	                     WHEN B.SCM_FAMILY_CD = 'SSD' THEN A.SOM_AVL_STRGY_AMT - (
                      															  	CASE WHEN C.RP_SOM_CD IS NOT NULL AND A.SOM_AVL_STRGY_AMT > 0
                                                                            			 THEN A.SOM_AVL_STRGY_QTY * C.DRAM_PRICE
	                                             									ELSE 0
	                                        										END
                      															 )
	                ELSE 0
	                END F_SOM_AVL_STRGY_AMT,
	                CASE WHEN B.SCM_FAMILY_CD = 'DRAM' THEN A.SOM_AVL_GNRAL_AMT
	                     WHEN B.SCM_FAMILY_CD = 'Hybrid' THEN CASE WHEN C.RP_SOM_CD IS NULL THEN A.SOM_AVL_GNRAL_AMT
	                            							  ELSE A.SOM_AVL_GNRAL_AMT * C.DRAM_RATE
	                       									  END
	                     WHEN B.SCM_FAMILY_CD = 'SSD' THEN CASE WHEN C.RP_SOM_CD IS NOT NULL AND A.SOM_AVL_GNRAL_AMT > 0
                       											THEN A.SOM_AVL_GNRAL_QTY * C.DRAM_PRICE
	                            						   ELSE 0
	                       								   END
	                     ELSE 0
	                END D_SOM_AVL_GNRAL_AMT,
	                CASE WHEN B.SCM_FAMILY_CD = 'NAND' THEN A.SOM_AVL_GNRAL_AMT
	                     WHEN B.SCM_FAMILY_CD = 'Hybrid' THEN A.SOM_AVL_GNRAL_AMT - (
                       																 	CASE WHEN C.RP_SOM_CD IS NULL THEN A.SOM_AVL_GNRAL_AMT
	                                             											 ELSE A.SOM_AVL_GNRAL_AMT * C.DRAM_RATE
	                                        											END
                       																)
	                     WHEN B.SCM_FAMILY_CD = 'SSD' THEN A.SOM_AVL_GNRAL_AMT - (
                       																CASE WHEN C.RP_SOM_CD IS NOT NULL AND A.SOM_AVL_GNRAL_AMT > 0
                                                                               			 THEN A.SOM_AVL_GNRAL_QTY * C.DRAM_PRICE
	                                             									ELSE 0
	                                        										END
                       															 )
	                     ELSE 0
	                END F_SOM_AVL_GNRAL_AMT,
	                CASE WHEN B.SCM_FAMILY_CD = 'DRAM' THEN A.SOM_RMA_AMT
	                     WHEN B.SCM_FAMILY_CD = 'Hybrid' THEN CASE WHEN C.RP_SOM_CD IS NULL THEN A.SOM_RMA_AMT
	                            							  ELSE A.SOM_RMA_AMT * C.DRAM_RATE
	                       									  END
	                     WHEN B.SCM_FAMILY_CD = 'SSD' THEN CASE WHEN C.RP_SOM_CD IS NOT NULL
                       											THEN A.SOM_RMA_QTY * C.DRAM_PRICE
	                            						   ELSE 0
	                       								   END
	                     ELSE 0
	                END D_SOM_RMA_AMT,
	                CASE WHEN B.SCM_FAMILY_CD = 'NAND' THEN A.SOM_RMA_AMT
	                     WHEN B.SCM_FAMILY_CD = 'Hybrid' THEN A.SOM_RMA_AMT - (
                       														   	CASE WHEN C.RP_SOM_CD IS NULL THEN A.SOM_RMA_AMT
	                                           										 ELSE A.SOM_RMA_AMT * C.DRAM_RATE
	                                      										END
                       														  )
	                     WHEN B.SCM_FAMILY_CD = 'SSD' THEN A.SOM_RMA_AMT - (
                       															CASE WHEN C.RP_SOM_CD IS NOT NULL
                                                                        			 THEN A.SOM_RMA_QTY * C.DRAM_PRICE
	                                           								    ELSE 0
	                                      										END
                       													   )
	                     ELSE 0
	                END F_SOM_RMA_AMT,
					A.SHIFT_APPLY_YN,
					A.PRE_LOOK_SHIFT_APPLY_YN,
					A.PRE_LOOK_SOM_SUM_QTY,
	                A.CRT_TM,
	                A.CRT_USER_ID,
	                A.CHG_TM,
	                A.CHG_USER_ID
	          FROM	RPI_SOM A,
	             	RPI_RP_SOM_CD_VW B,
	             	RPR_MCP_SSD_DIST_RATE_PLN C
	         WHERE	A.RP_SOM_CD  	  = B.RP_SOM_CD
	           AND  A.RP_SOM_CD  	  = C.RP_SOM_CD(+)
               AND  A.PLN_YM          = C.PLN_YM(+)
               AND  A.PLN_WEEK_GBN_CD = C.PLN_WEEK_GBN_CD(+)
               AND  A.TGT_YM          = C.TGT_YM(+)
               --AND  A.RP_SOM_CD NOT LIKE '%HBM%' -- 2021.11.30
               --AND  A.RP_SOM_CD NOT IN ('DA_0G_HBM3_1ST_TSV 12DP_C','DA_0G_HBM3_1ST_TSV ODP_C','DA_16G_HBM2E_1ST_TSV ODP_C','DA_16G_HBM2E_1ST_TSV QDP_C','DE_8G_HBM2_2ND_TSV ODP_C','DE_8G_HBM2_2ND_TSV QDP_C') -- 2021.11.30
               --AND A.RP_SOM_CD NOT IN (SELECT DISTINCT RP_SOM_CD FROM STI_RPCODE_M WHERE RP_SOM_CD LIKE '%HBM%' AND RP_SOM_CD NOT IN ('DA_16G_HBM3_1ST_TSV ODP_C','DA_16G_HBM3_1ST_TSV 12DP_C'))
               --AND A.RP_SOM_CD NOT IN (SELECT DISTINCT RP_SOM_CD FROM STI_RPCODE_M WHERE RP_SOM_CD LIKE '%HBM%' AND RP_SOM_CD NOT IN ('DA_16G_HBM3_1ST_TSV ODP_C','DA_16G_HBM3_1ST_TSV 12DP_C'))
        ) A,
        (
       		SELECT	SCM_FAMILY_CD
                   ,RP_SOM_CD
                   ,PKG_TYP_CD2
                   ,UNIT_STRUCT_CD
                   ,SUB_RP_SOM_CD
                   ,SUB_RP_SOM_CNT
                   ,SUB_SCM_FAMILY_CD
                   ,BOM_STAT_CD
                   ,DEL_YN
                   ,AMT_DIST_TGT_YN
			       ,CASE WHEN MCPSSD_DRAM_LOOSE_QTY IS NULL THEN 1
						 WHEN MCPSSD_DRAM_LOOSE_QTY = 0 THEN 1
				    ELSE MCPSSD_DRAM_LOOSE_QTY
                    END AS MCPSSD_DRAM_LOOSE_QTY
			       ,CASE WHEN MCPSSD_FLASH_LOOSE_QTY IS NULL THEN 1
				         WHEN MCPSSD_FLASH_LOOSE_QTY = 0 THEN 1
					ELSE MCPSSD_FLASH_LOOSE_QTY
                  	END AS MCPSSD_FLASH_LOOSE_QTY
			       ,CASE WHEN DRAM_LOOSE_QTY IS NULL THEN 1
						 WHEN DRAM_LOOSE_QTY = 0 THEN 1
				    ELSE DRAM_LOOSE_QTY
                    END AS DRAM_LOOSE_QTY
			       ,CASE WHEN DRAM_LOOSE_ALL_QTY IS NULL THEN 1
					     WHEN DRAM_LOOSE_ALL_QTY = 0 THEN 1
				    ELSE DRAM_LOOSE_ALL_QTY
                  	END AS DRAM_LOOSE_ALL_QTY
              FROM	(
				     	SELECT	SCM_FAMILY_CD
			                   ,RP_SOM_CD
			                   ,PKG_TYP_CD2
			                   ,UNIT_STRUCT_CD
			                   ,SUB_RP_SOM_CD
			                   ,SUB_RP_SOM_CNT
			                   ,SUB_SCM_FAMILY_CD
			                   ,BOM_STAT_CD
			                   ,DEL_YN
			                   ,AMT_DIST_TGT_YN
							   ,SUM(CASE WHEN SCM_FAMILY_CD IN ('Hybrid', 'SSD') AND SUB_SCM_FAMILY_CD = 'DRAM'  THEN 1 ELSE 0 END) OVER (PARTITION BY SCM_FAMILY_CD, RP_SOM_CD) AS MCPSSD_DRAM_LOOSE_QTY
							   ,SUM(CASE WHEN SCM_FAMILY_CD IN ('Hybrid', 'SSD') AND SUB_SCM_FAMILY_CD = 'NAND' THEN 1 ELSE 0 END) OVER (PARTITION BY SCM_FAMILY_CD, RP_SOM_CD) AS MCPSSD_FLASH_LOOSE_QTY
--                        	   ,SUM(
--										CASE WHEN SCM_FAMILY_CD = 'DRAM' AND SUB_RP_SOM_CD NOT LIKE '%#_BASE%' ESCAPE '#' AND SUB_RP_SOM_CD NOT LIKE '%BASE#_%' ESCAPE '#' THEN 1
--							            ELSE 0
--							            END
--								   ) OVER (PARTITION BY SCM_FAMILY_CD, RP_SOM_CD) AS DRAM_LOOSE_QTY
--                        	   ,SUM(
--										CASE WHEN SCM_FAMILY_CD = 'DRAM' THEN 1
--							            ELSE 0
--							            END
--								   ) OVER (PARTITION BY SCM_FAMILY_CD, RP_SOM_CD) AS DRAM_LOOSE_ALL_QTY
                                ,CASE WHEN SCM_FAMILY_CD = 'DRAM' THEN SUB_RP_SOM_CNT ELSE 0 END AS DRAM_LOOSE_QTY -- 2021.11.30
                                ,SUM(CASE WHEN SCM_FAMILY_CD = 'DRAM' THEN SUB_RP_SOM_CNT ELSE 0 END) OVER (PARTITION BY SCM_FAMILY_CD, RP_SOM_CD) AS DRAM_LOOSE_ALL_QTY -- 2021.11.30
				          FROM	COM_ADM.STI_RP_SOM_CD_SPLIT_VW T1 -- 2021.11.30
					)
		) B
 WHERE	A.RP_SOM_CD = B.RP_SOM_CD(+)
;

--CREATE PUBLIC SYNONYM RPI_SOM_MG_VW_TEST_MKH FOR RPLS_ADM.RPI_SOM_MG_VW_TEST_MKH;

--GRANT SELECT ON RPLS_ADM.RPI_SOM_MG_VW_TEST_MKH TO COM_ADM WITH GRANT OPTION;

--GRANT SELECT ON RPLS_ADM.RPI_SOM_MG_VW_TEST_MKH TO COM_APP WITH GRANT OPTION;

--GRANT SELECT ON RPLS_ADM.RPI_SOM_MG_VW_TEST_MKH TO RPLS_APP WITH GRANT OPTION;
