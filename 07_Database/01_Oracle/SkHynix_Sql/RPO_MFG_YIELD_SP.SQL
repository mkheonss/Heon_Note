/*------------------------------------------------------------------------------
-- 개체 이름: RPLS_ADM.RPO_MFG_YIELD_SP
-- 만든 날짜: 2019-08-28 오후 5:16:16
-- 마지막 수정 날짜: 2023-11-21 오후 2:31:46
-- 상태: VALID
------------------------------------------------------------------------------*/
CREATE OR REPLACE PROCEDURE RPLS_ADM."RPO_MFG_YIELD_SP"
(
    VI_PLN_REV      IN VARCHAR2 DEFAULT NULL,
    VI_CUM_GUBUN    IN VARCHAR2 DEFAULT NULL,
    VI_RETURN_VALUE IN OUT VARCHAR2
)
IS
/*******************************************************************
    -. FUNCTION    : RPO_MFG_YIELD_SP
    -. PROGRAMMER  : 김준수
    -. CREATE_DATE : 2019. 08. 28
    -. DESCRIPTION : 생산계획요약조회용 YIELD 정보를 RP수율에서 INTERFACE
    -. ARGUMENT    :
    -. HISTORY LOGIC
        MODIFIED DATE  MODIFIED   VERSION   DESCRIPTION
        2019.08.28     김준수     1.0        신규작성
        2019.09.05     김준수     1.0        화면에서 저장하는 루틴추가.(VI_CUM_GUBUN)
        2019.10.08     표영택                CUM 대상 중복때문에 ORG FAMILY 조건 추가
        2019.10.08     김준수                FAB, WFT는  생산계획에 있는것만 대상추가.
        2019.10.24     김준수                Family, Fab별 cum1값 추가.
        2019.10.25     김준수                'BGASSD' ORG FAMILY에 추가.
        2019.10.28     김준수                flash인경우  mode상관없이 apply_yn 설정
        2019.10.30     김준수                pt에서 생산량이 없는경우 처리  로직 추가.
        2019.11.13     김준수                복합fab제외, flash wfwt에서 nand만, iTLC는 TLC로 합병.
        2019.11.15     김준수                'HBM'처리를 cum선택할수 있게함. CUM1,CUM2수율계산시 FAB,WFT값이 없으면 0으로 처리.
        2019.11.19     김준수                org family 'SSD'표기, p&t 계산시 pkg가 0일시 0으로 처리함.
        2019.11.20     김준수                Net Die 300 Cnt 없는것은  있는값으로  통합해서 계산함.
        2019.11.21     김준수                TLC,iTLC 합병하되, cum선정시는 TLC로 구분함.
        2019.11.25     김준수                tech,fabDens,Cell,p.ver,mode가 생산에 수량없으면, 제외함.
        2019.11.28     김준수                수량 체크시 BIZ TYPE 단품,모듈만 적용되게함.
        2019.12.02     김준수                p&t 로직의 가중평균, 산술평균 pkg,pkt 나누어져 합병 적용.
        2019.12.05     김준수                p&t 산술평균 pkg,pkt(wlp,portion) 복합제품 로직 변경.
        2019.12.13     김준수                cum대상 선정시 최신Release버젼의 대상으로 가져옴.
        2019.12.19     김준수                FAB,WFT 수율가져올시 생산수량에서 MODE는 상관없이 가져옴.
        2019.12.27     표영택                SP 향 FLASH 도 제외, WAFER BIZ 추가
        2020.03.30     김준수                HBM관련 NETDIE를 WTF수량 가져오는 부분에서 가져오도록 수정.
        2020.03.31     김준수                P&T 의 Raw NAND부분 수정, SCM_PKG_TYP_CD4 컬럼 추가.
        2020.04.07     김준수                SCM_PKG_TYP_CD4 컬럼 추가한것을 TSV_GBN_CD 컬럼으로 대처함.
        2020.06.18     김정훈                Family, FAB 별 CUM1 수율 제거 -- 20200630 원복
        2020.08.13     김준수                TSV_GBN_CD 컬럼을  NVL(TSV_GBN_CD,SCM_PKG_TYP_CD4) 수정함.
        2020.11.05     정헌식                WFT 수율에 LAD2 CD가 생성되어 있어, WFT 수율 산출시 LAD2 제외 LOGIC 반영함.
        2021.01.13     정헌식                FAB2_CD 기반으로 MAX(YLD)사용, HBM 별도처리 제외 등 현업요건 다수 반영.
        2021.02.15     최대한                SR20210219261 RP - 생산계획요약조회 - 수율 TAB 특수 제품 WFT 수율 산출 Logic 변경
        2021.04.14     정헌식                TSV 제품 FAB, WFT 구분에 의한 수정
        2021.06.23     김준수                output data생성>제품 Mix Data 생성 이하 배치 실행 로그 설정
        2021.08.27     정헌식                SP.향만 있는 제품에 대한 FAB 수율 반영을 위한 Logic 수정
        2021.09.01     정헌식                2406B Stack 구분 및 POP 제품 통합 반영
        2022.01.19     김정훈                속도 이슈로 RPI_RPBOM_TREE_I -> RPI_RPBOM_I 로 변경
        2022.04.13     정헌식                MODE에 'DIMM' 생성되는 현상 조치
        2022.09.02     정헌식                RDL 별도 수율 미반영 기인 조치
        2022.11.08     최윤규                [CUM1,2 YIELD INSERT] 동일 주키에 대해, 두개의 YLD 존재로 인해 MAX로 임시 처리
        2022.11.29     정헌식                NAND DIE 수율 대상 제품 LAD2 PORTION 반영
        2023.06.14     마경헌         			  TSV 분리작업으로 변경 - (20230614)
        2023.10.12		 마경헌				        NAND의 경우 별도의 'Total' 추가하여 데이터를 생성하고 Cum1, Cum2를 계산하도록 변경.
        2023.10.12		 마경헌				        GBN_CD 구분 조건 로직 변경.
        2023.11.21     마경헌                P_T에 대해 TSV(Module) 제품과 분리하여 수율계산하도록 변경.
*******************************************************************/

/** LOG 에 사용하는 변수 **/
    V_CURRDATE             DATE;                /* 현재시간 정의 */
    V_PLN_DT        VARCHAR2(8);
    V_REV_NO        VARCHAR2(50);
/** 현재 REV에 사용하는 변수 **/

    V_PLN_REV         VARCHAR2(50);             /* 현재 REV 정의*/

    V_PLN_YM          VARCHAR2(6);              /* 현재 년월 정의*/
    V_PLN_WEEK_GBN_CD VARCHAR2(50);             /* 현재 주차 정의 */

    V_PLN_START_YM    VARCHAR2(6);              /* 계획시작 년월 정의*/
    V_PLN_END_YM      VARCHAR2(6);              /* 계획종료 년월 정의*/
    V_REF_SYS_ID      VARCHAR2(50);             /* 참조시스템ID */
	  V_REF_PLN_REV     VARCHAR2(50);             /* 참조계획리비전 */
	  V_COPY_START_YM   VARCHAR2(6);              /* 복사시작 년월 정의*/
    V_COPY_END_YM     VARCHAR2(6);              /* 복사종료 년월 정의*/
    V_FCT_START_YM    VARCHAR2(6);              /* 예상데이터반영시작년월 정의*/
    V_FCT_END_YM      VARCHAR2(6);              /* 예상데이터반영종료 년월 정의*/
    V_COPY_CNT        NUMBER;                   /* 마지막월 복사할 개월수*/
    V_CUM_GUBUN       CHAR(1);
    V_BEF_PLN_REV    VARCHAR2(50);              /* 최신주차의 RELEASE 버젼가져오기 */

    V_MCATG_PRGS_STAT_CD RPI_PLN_REV_STAT.MCATG_PRGS_STAT_CD%TYPE := '';
    V_SCATG_PRGS_STAT_CD RPI_PLN_REV_STAT.SCATG_PRGS_STAT_CD%TYPE := '';
    V_WORK_LCATG_CD      RPI_PLN_REV_STAT.WORK_LCATG_CD%TYPE := 'L03';
    V_WORK_MCATG_CD      RPI_PLN_REV_STAT.WORK_MCATG_CD%TYPE := 'M06';
    V_WORK_SCATG_CD      RPI_PLN_REV_STAT.WORK_SCATG_CD%TYPE := '';
    V_RETURN_VALUE       VARCHAR2(200) := '';

    USER_DEFINE_ERROR EXCEPTION;

BEGIN

    /* ============================================================================================== */
    /*  로그처리                                                                                        */
    /* ============================================================================================== */
    SELECT SYSDATE INTO V_CURRDATE FROM DUAL;                                                                /* 현재시간 정의 */

    SELECT TO_CHAR(SYSDATE,'YYYYMMDD'),'RP_'|| (SELECT SUBSTR(WORK_YW, 5, 2) AS CUR_WEEK FROM MAD_CALENDAR WHERE WORK_DT = TO_CHAR(SYSDATE, 'YYYYMMDD')) || '_' || TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS')
    INTO V_PLN_DT, V_REV_NO                                                                                    /* 로그용 키값 정의 */
    FROM DUAL;

    -- PLN REV 상태값 UPDATE
    V_MCATG_PRGS_STAT_CD := 'R';  -- 중분류 RUNNING
    V_SCATG_PRGS_STAT_CD := 'R';  -- 소분류 RUNNING
    V_WORK_SCATG_CD      := '10'; -- RPO_MFG_YIELD_SP
--    01 : RPO_SALE_PSI_RP           05 : RPO_EQP_OPRATIO_TOT_CAPA_SP
--    02 : RPO_LINE_MFG_PSI_SP       06 : RPO_BOH_SP
--    03 : RPO_SOM_DSATIS_CAUSE_SP   07 : RPO_WF_TEST_OUT_SP
--    04 : RPO_SITE_LINE_MFG_PLN_SP  08 : RPO_FGS_IN_PLAN_ADJUST_SP
--    09 : RPO_WF_TEST_OUT_PEG_SP    10 : RPO_MFG_YIELD_SP

    V_CUM_GUBUN :=  VI_CUM_GUBUN;


    IF V_CUM_GUBUN <> 'Y'  THEN
    	RPLS_ADM.RPI_PLN_REV_STAT_UPDATE_SP ( VI_PLN_REV, V_MCATG_PRGS_STAT_CD, V_SCATG_PRGS_STAT_CD, V_WORK_LCATG_CD, V_WORK_MCATG_CD, V_WORK_SCATG_CD, V_RETURN_VALUE );
    	COMMIT;
    END IF;

    RPLS_ADM.RPL_PROG_LOG(V_REV_NO||'-'||VI_PLN_REV||'-'||VI_CUM_GUBUN, V_PLN_DT, 'RPO_MFG_YIELD_TABLE', 'RPO_MFG_YIELD_SP', 'S', 'WORK_START');  /* START LOG [필수] */
    COMMIT;

    /* ============================================================================================== */
    /*  초기 키값 설정                                                                                */
    /* ============================================================================================== */
    /* 계획REVISION, 계획년월, 계획주차수 구함 */

    SELECT PLN_REV, PLN_YM, PLN_WEEK_GBN_CD
      INTO V_PLN_REV, V_PLN_YM, V_PLN_WEEK_GBN_CD
      FROM RPI_PLN_REV
     WHERE PLN_REV = VI_PLN_REV
    ;

		V_PLN_REV := VI_PLN_REV;

		-- 계획구간 및 COPY 구간에 대한 변수 설정, 최신주차의 릴리즈 버젼 가져오기.
    SELECT A.PLN_START_YM, A.PLN_END_YM, A.PLN_START_YM, To_Char(Add_Months(To_Date(A.PLN_END_YM,'YYYYMM'),4),'YYYYMM'), C.PLN_REV
      INTO V_PLN_START_YM, V_PLN_END_YM, V_FCT_START_YM, V_FCT_END_YM, V_BEF_PLN_REV
      FROM RPI_PLN_REV A
         , RPI_PLN_REV C
     WHERE A.PLN_REV = V_PLN_REV
    	 AND C.PLN_REV = (
       										SELECT MAX(PLN_REV) AS BEF_PLN_REV
                         	  FROM RPI_PLN_REV
                           WHERE SYS_ID = 'R'
                             AND PLN_REV < A.PLN_REV
                             AND RLS_YN = 'R'
                        )
    ;

    /****************************************************************************/
    /*  로직 흐름 정리                                                          */
    /*--------------------------------------------------------------------------*/
    /****************************************************************************/

    IF V_BEF_PLN_REV IS NULL OR V_BEF_PLN_REV = '' THEN
    		V_BEF_PLN_REV := '-';
    END IF;

    DBMS_OUTPUT.PUT_LINE('**********[ START YIELD INSERT  ] **********'||'-'|| TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS'));
    DBMS_OUTPUT.PUT_LINE('********** V_BEF_PLN_REV:' || V_BEF_PLN_REV||'-'|| TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS'));

    -- #######################################################################################################################################################################################
   	IF V_CUM_GUBUN <> 'Y'  THEN
    		-- 기존 데이터 삭제
        DELETE
          FROM   RPO_MFG_YIELD
         WHERE  PLN_REV = V_PLN_REV;

       	DBMS_OUTPUT.PUT_LINE('**********[ FAB YIELD INSERT  ] **********'||'-'|| TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS'));

       	-- 01. FAB YIELD INSERT
       	INSERT INTO RPO_MFG_YIELD(
        						  		  		  	PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD
                  								, NET_DIE_300_CNT, LINE_GRP_CD, TSV_GBN_CD, PKG_TYP_CD2,PNT_PLN_SPCL_CD
                                  , ORG_SCM_FAMILY_CD, TGT_YM, PLN_YM, PLN_WEEK_GBN_CD, YLD, FAB2_CD, CUM_YLD_APPLY_TGT_YN
                                  , SORT_SEQ, CRT_TM, CRT_USER_ID, CHG_TM, CHG_USER_ID
                                 )
       	WITH FAB_DRAM_PORTION AS
        (
        		SELECT PLN_REV, PRTN_TYP_CD, LINE_CD, FAB_ID, FAB2_CD, TGT_YM, DECODE(MAX(YLD), 0, 1, MAX(YLD)) AS YLD
            	FROM (
              				SELECT PLN_REV, PRTN_TYP_CD, LINE_CD, FAB_ID, RP_CD, PROD_GRP_CD, PRTN_DATA_GBN_CD, TGT_YM
                        		/* 아래로 변경함(김정훈TL님 변경요청-2019.09.11) */
                        		--, (1-NVL(YLD,0)) AS YLD
		                     	 , CASE WHEN PROD_GRP_CD = 'NK' THEN (1-NVL(YLD,0)) ELSE NVL(YLD,1) END AS YLD
                        	 , FAB2_CD
                			  FROM RPI_PORTION
              				 WHERE PLN_REV = V_PLN_REV
                				 AND PRTN_TYP_CD = 'WAFER'
                				 AND LINE_CD = 'WFT'
                				 AND PRTN_DATA_GBN_CD = 'PLN'
                   )
           	 GROUP BY PLN_REV, PRTN_TYP_CD, LINE_CD, FAB_ID, FAB2_CD, TGT_YM
       	) --★★ 2021.01.13 FAB2_CD를 KEY로 MAX값 반영되도록 수정
        , FAB_FLASH_PORTION AS
        (
        		SELECT A.PLN_REV, A.PRTN_TYP_CD, A.LINE_CD, A.FAB_ID, A.FAB2_CD/*, A.RP_CD, A.PROD_GRP_CD, A.PRTN_DATA_GBN_CD */
                 , A.TGT_YM, CASE WHEN (A.YLD + NVL(B.YLD,0)) > 1 THEN 1 ELSE (A.YLD + NVL(B.YLD,0)) END AS YLD  --★★ 1 이상은 1로 반영되도록 수정
            	FROM FAB_DRAM_PORTION A
                 , (
                  		SELECT PLN_REV, FAB_ID, FAB2_CD, TGT_YM, MAX(YLD) AS YLD
                     	  FROM RPI_PORTION
                       WHERE PLN_REV = V_PLN_REV
                         AND LINE_CD = 'WFT'
                         AND PRTN_DATA_GBN_CD = 'PLN'
                         AND PRTN_TYP_CD = 'LPGD'
                       GROUP BY PLN_REV, FAB_ID, FAB2_CD, TGT_YM
                   ) B   -- ★★ FAB2_CD를 KEY로 MAX값 반영되도록 수정
          	 WHERE 1 = 1
	             /*
               AND   A.PLN_REV = B.PLN_REV(+)
	             AND   A.LINE_CD = B.LINE_CD(+)
	             AND   A.FAB_ID = B.FAB_ID(+)
	             AND   A.RP_CD = B.RP_CD(+)
	             AND   A.PROD_GRP_CD = B.PROD_GRP_CD(+)
	             AND   A.PRTN_DATA_GBN_CD = B.PRTN_DATA_GBN_CD(+)
               */  																								--★★ 2021.01.13 FAB2 CD를 KEY로 JOIN
	             AND   A.TGT_YM = B.TGT_YM(+)
	             /*AND   B.PRTN_TYP_CD (+)= 'LPGD'*/  							--★★ 2021.01.13 FAB2 CD를 KEY로 JOIN
	             AND   A.FAB2_CD = B.FAB2_CD(+)
	             /* AND  (A.YLD + NVL(B.YLD,0)) <= 1   PORTION이 1 이하인것으로 가져옴.   20200611 by  js.kim  */  --★★ 2021.01.13 SELECT문에서 1로 치환 반영
       	)
       	, WFT_MFG_TBL AS
        (
            SELECT B.SCM_FAMILY_CD, B.FAB_ID, B.TECH_CD, B.FAB_DEN_CD, NVL(B.CELL_LAYER_TYP_CD,'*') AS CELL_LAYER_TYP_CD
                 , NVL(B.SCM_PROD_VER_CD,'*') AS SCM_PROD_VER_CD
               	 , CASE WHEN B.SCM_FAMILY_CD = 'NAND' THEN 'Raw NAND' ELSE B.CHG_PROD_MODE_CD END AS CHG_PROD_MODE_CD -- ★★ 2021.01.13 NAND는 MODE를 Raw NAND로 치환
               	 , CASE WHEN B.SCM_PKG_TYP_CD4 = 'TSV' THEN 'TSV' ELSE '*' END AS SCM_PKG_TYP_CD4 --21.04.14 JHS TSV 구분을 위한 구분자 추가
               	 , MIN(A.TGT_YM) AS MIN_TGT_YM, MAX(A.TGT_YM) AS MAX_TGT_YM, SUM(A.DATA_VAL)   --★★ 2021.01.13 DATA 조회 조건에 TGT_YM 포함하기 위해 MIN, MAX 설정
           	  FROM RPO_LINE_MFG_PLN_MG_VW A, (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') B
                 , RPI_PLN_REV C   --★★ PLN_REV 구간만 DATA INSERT하기 위해 참조
           	 WHERE 1 = 1
             	 AND A.PLN_REV = V_PLN_REV
             	 AND C.PLN_REV = A.PLN_REV
             	 AND A.RP_CD = B.RP_CD
             	 AND A.LINE_MIX_CD = 'WFT'
             	 AND A.PLN_TYP_CD = 'OUT'
             	 AND A.UNIT_CD = 'SLS'    --★★ WFT OUT 기준만 반영
             	 AND NVL(B.CHG_BIZ_TYP_CD,'*') = '*'
             	 AND A.TGT_YM BETWEEN C.PLN_START_YM AND C.PLN_END_YM   --★★ 2021.01.13 PLN_REV 구간만 DATA 생성하기 위해 추가
             GROUP BY B.SCM_FAMILY_CD, B.FAB_ID, B.TECH_CD, B.FAB_DEN_CD, NVL(B.CELL_LAYER_TYP_CD,'*'), NVL(B.SCM_PROD_VER_CD,'*')
                	, CASE WHEN B.SCM_FAMILY_CD = 'NAND' THEN 'Raw NAND' ELSE B.CHG_PROD_MODE_CD END -- ★★  2021.01.13 NAND는 MODE를 Raw NAND로 치환
                	, CASE WHEN B.SCM_PKG_TYP_CD4 = 'TSV' THEN 'TSV' ELSE '*' END --21.04.14 JHS TSV 구분을 위한 구분자 추가
             HAVING SUM(A.DATA_VAL) > 0
       	)
       	SELECT V_PLN_REV AS PLN_REV, D.SCM_FAMILY_CD, C.FAB_ID, NVL(D.TECH_CD,' ') AS TECH_CD, NVL(D.FAB_DEN_CD,' ') AS FAB_DEN_CD, NVL(D.CELL_LAYER_TYP_CD,' ') AS CELL_LAYER_TYP_CD

        		 --■■■ 로직변경(2023.10) - , NVL(D.CHG_PROD_MODE_CD,' ') AS CHG_PROD_MODE_CD
             , NVL(DECODE(UPPER(D.CHG_PROD_MODE_CD), 'RAW NAND', 'Total', D.CHG_PROD_MODE_CD), '*') AS CHG_PROD_MODE_CD

             , NVL(D.SCM_PROD_VER_CD,' ') AS SCM_PROD_VER_CD
             , MAX(NVL(D.NET_DIE_300_CNT,0)) AS NET_DIE_300_CNT, C.LINE_GRP_CD, NVL(NVL(D.TSV_GBN_CD,D.SCM_PKG_TYP_CD4),' ') AS TSV_GBN_CD, NVL(D.PKG_TYP_CD2,' ') AS PKG_TYP_CD2
             , NVL(D.PNT_UNUS_OPER_VAL,' ') AS PNT_PLN_SPCL_CD, D.SCM_FAMILY_CD AS ORG_SCM_FAMILY_CD, C.TGT_YM, V_PLN_YM AS PLN_YM, V_PLN_WEEK_GBN_CD AS PLN_WEEK_GBN_CD
             , Max(C.YLD * DECODE(D.SCM_FAMILY_CD,'DRAM',NVL(E.YLD,1),'NAND',NVL(F.YLD,1),1)) AS YLD
             , REPLACE(REPLACE(MAX(C.RP_CD), '_TSV_', '_'), '_SP_', '_') AS FA2_CD  --21.04.14 TSV는 FAB2 CD를 NON_TSV로 추가  --21.08.27 NORMAL 제품이 없는 경우도 있어 SP.향도 포함하도록 수정
             , '' AS CUM_YLD_APPLY_TGT_YN, 0 AS SORT_SEQ ,SYSDATE AS CRT_TM, 'MFG_YIELD_SP' AS CRT_USER_ID, '' AS CHG_TM, '' AS CHG_USER_ID
       		FROM  --(SELECT DISTINCT FA2_CD FROM RPI_FGS_COMP_BOM) A
               RPI_YIELD C
             , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN='Y') D
             /*, FGS_MFG_TBL G */
             , WFT_MFG_TBL G    -- ★★ 2021.01.13  DATA 생성에 대한 제약을 FGS -> WFT 생산 기준으로 변경
             , FAB_DRAM_PORTION E
             , FAB_FLASH_PORTION F
         WHERE 1 = 1
           AND C.PLN_REV = V_PLN_REV
       		 AND C.LINE_GRP_CD = 'FAB'
       		 AND C.YLD_GBN_CD = 'PLN'
     			 --AND A.FA2_CD = C.RP_CD    -- BOM에 있는 RP_CD만 대상으로함.
       		 AND C.RP_CD = D.RP_CD
       		 AND D.SCM_FAMILY_CD = G.SCM_FAMILY_CD     -- FGS 생산계획에 있는 수율만 대상으로함.
       		 AND D.FAB_ID = G.FAB_ID
       		 AND D.TECH_CD = G.TECH_CD
       		 AND D.FAB_DEN_CD = G.FAB_DEN_CD
       		 AND NVL(D.CELL_LAYER_TYP_CD,'*') = NVL(G.CELL_LAYER_TYP_CD,'*')
		       AND NVL(D.SCM_PROD_VER_CD,'*') = NVL(G.SCM_PROD_VER_CD,'*')
		       AND D.CHG_PROD_MODE_CD = G.CHG_PROD_MODE_CD   --★★ MODE도 MAPPING 되도록 수정 필요
		       AND NVL(D.SCM_PKG_TYP_CD4, '*') = G.SCM_PKG_TYP_CD4  --21.04.14  JHS  TSV 구분자를 위한 제약 추가
		       AND C.TGT_YM BETWEEN G.MIN_TGT_YM AND G.MAX_TGT_YM   --★★ 월별 WFT OUT의 MIN, MAX 사이에 수율만 보이도록 반영
		       AND C.RP_CD = E.FAB2_CD(+)
		       AND C.TGT_YM = E.TGT_YM(+)
		       AND C.RP_CD = F.FAB2_CD(+)
		       AND C.TGT_YM = F.TGT_YM(+)
         GROUP BY D.SCM_FAMILY_CD, C.FAB_ID, NVL(D.TECH_CD,' '), NVL(D.FAB_DEN_CD,' '), NVL(D.CELL_LAYER_TYP_CD,' ')
         				--■■■ 로직변경(2023.10) , NVL(D.CHG_PROD_MODE_CD,' ')
         			  , NVL(DECODE(UPPER(D.CHG_PROD_MODE_CD), 'RAW NAND', 'Total', D.CHG_PROD_MODE_CD), '*')
                , NVL(D.SCM_PROD_VER_CD,' ')
                , C.LINE_GRP_CD, NVL(NVL(D.TSV_GBN_CD,D.SCM_PKG_TYP_CD4),' '), NVL(D.PKG_TYP_CD2,' ') ,NVL(D.PNT_UNUS_OPER_VAL,' '), C.TGT_YM --, B.FA2_CD
       	HAVING MAX(C.YLD * DECODE(D.SCM_FAMILY_CD,'DRAM',NVL(E.YLD,1),'NAND',NVL(F.YLD,1),1)) > 0
       	;

      	DBMS_OUTPUT.PUT_LINE('**********[ WFT YIELD INSERT  ] **********'||'-'|| TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS'));

       	-- 02. WFT YIELD INSERT
        INSERT INTO RPO_MFG_YIELD(
	        							  		  		PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD
	        												, NET_DIE_300_CNT, LINE_GRP_CD, TSV_GBN_CD, PKG_TYP_CD2, PNT_PLN_SPCL_CD
	                                , ORG_SCM_FAMILY_CD, TGT_YM, PLN_YM, PLN_WEEK_GBN_CD, YLD, FAB2_CD, CUM_YLD_APPLY_TGT_YN
	                                , SORT_SEQ, CRT_TM, CRT_USER_ID, CHG_TM, CHG_USER_ID
                                 )
       	WITH WFT_DRAM_PORTION AS
        (
        		SELECT PLN_REV, PRTN_TYP_CD, LINE_CD, FAB_ID, RP_CD, PROD_GRP_CD, PRTN_DATA_GBN_CD, TGT_YM, (1-NVL(YLD,0)) AS YLD , FAB2_CD
              FROM RPI_PORTION
          	 WHERE PLN_REV = V_PLN_REV
            	 AND PRTN_TYP_CD = 'GRADE'
            	 AND LINE_CD = 'WFT'
            	 AND PRTN_DATA_GBN_CD = 'PLN'
       	)
       	, WFT_FLASH_PORTION AS
        (
           	SELECT PLN_REV, PRTN_TYP_CD, LINE_CD, FAB_ID, RP_CD, PROD_GRP_CD, PRTN_DATA_GBN_CD, TGT_YM, (1-NVL(YLD,0)) AS YLD , FAB2_CD
            	FROM RPI_PORTION
          	 WHERE PLN_REV = V_PLN_REV
            	 AND PRTN_TYP_CD = 'GRADE'
            	 AND LINE_CD = 'PKG'
            	 AND PRTN_DATA_GBN_CD = 'PLN'
       	)
       	-- ★★ 2021.01.13  NORMAL 제품 생산 제약 반영
       	, WFT_NORM_MFG_TBL AS
        (
            SELECT A.PLN_REV, A.WT_CD, MIN(A.WT_OUT_PLN_YM) AS MIN_TGT_YM, MAX(A.WT_OUT_PLN_YM) AS MAX_TGT_YM
                 , '-' AS PKG_TYP_CD2, CASE WHEN A.SCM_PKG_TYP_CD4 = 'TSV' THEN 'TSV' ELSE '*' END AS SCM_PKG_TYP_CD4 --21.04.14 JHS TSV 구분
                 , SUM(A.WT_OUT_PLN_ADJUST_QTY) AS PLN_QTY
            	FROM RPO_WF_TEST_OUT_PEG A
                 , RPI_PLN_REV B
             WHERE A.PLN_REV = V_PLN_REV
               AND B.PLN_REV = A.PLN_REV
               AND A.WT_OUT_PLN_YM BETWEEN B.PLN_START_YM AND B.PLN_END_YM
               AND (A.WT_CD, A.PKG_TYP_CD2, A.SCM_PKG_TYP_CD4) NOT IN
																									                    (
																											                    SELECT DISTINCT B.FR_RP_CD, B.PKG_TYP_CD2, NVL(B.SCM_PKG_TYP_CD4, '-')
																											                      FROM RPI_YIELD A
																											                         , (
																													                         SELECT DISTINCT A.TO_RP_CD, A.FR_RP_CD, M1.PKG_TYP_CD2, M1.SCM_PKG_TYP_CD4
																													                         FROM RPI_RPBOM_I A, (SELECT * FROM STI_RPCODE_M WHERE SCM_FAMILY_CD = 'DRAM' AND NEW_YN = 'Y') M1
																													                         WHERE A.LINE_CD = 'PKG'
																													                         AND A.USE_YN = 'Y'
																													                         AND A.TO_RP_CD = M1.RP_CD
																											                         	 ) B
																											                     WHERE A.PLN_REV = V_PLN_REV
																											                       AND A.YLD_GBN_CD = 'PLN'
																											                       AND A.LINE_GRP_CD = 'DIE'
																											                       AND A.YLD > 0 AND A.YLD < 1
																											                       AND A.RP_CD = B.TO_RP_CD
																									                    )
             GROUP BY A.PLN_REV, A.WT_CD, CASE WHEN A.SCM_PKG_TYP_CD4 = 'TSV' THEN 'TSV' ELSE '*' END
             HAVING SUM(A.WT_OUT_PLN_ADJUST_QTY) >= 1
        )
        -- ★★  2021.01.13  DIE 수율 제품 생산 제약 반영
        , WFT_SPCL_MFG_TBL AS
        (
        		SELECT A.PLN_REV, A.WT_CD, MIN(A.WT_OUT_PLN_YM) AS MIN_TGT_YM, MAX(A.WT_OUT_PLN_YM) AS MAX_TGT_YM
                 , NVL(A.PKG_TYP_CD2, '-') AS PKG_TYP_CD2, NVL(A.SCM_PKG_TYP_CD4, '-') AS SCM_PKG_TYP_CD4, SUM(A.WT_OUT_PLN_ADJUST_QTY) AS PLN_QTY
              FROM RPO_WF_TEST_OUT_PEG A
                 , RPI_PLN_REV B
             WHERE A.PLN_REV = V_PLN_REV
               AND B.PLN_REV = A.PLN_REV
               AND A.WT_OUT_PLN_YM BETWEEN B.PLN_START_YM AND B.PLN_END_YM
               AND (A.WT_CD, A.PKG_TYP_CD2, A.SCM_PKG_TYP_CD4) IN
																							                    (
																									                    SELECT DISTINCT
                                                                      			 CASE WHEN B.SCM_PKG_TYP_CD4 IS NOT NULL THEN REPLACE(REPLACE(B.FR_RP_CD, B.SCM_PKG_TYP_CD4||'_', ''), 'WLP', 'WT')
																									                        				ELSE B.FR_RP_CD
                                                                             END AS WT_CD, B.PKG_TYP_CD2, NVL(B.SCM_PKG_TYP_CD4, '-')  --22.09.02 RDL 별도 수율 미반영 기인 조치
																									                      FROM RPI_YIELD A
																									                         , (
																											                         SELECT DISTINCT A.TO_RP_CD, A.FR_RP_CD, M1.PKG_TYP_CD2, M1.SCM_PKG_TYP_CD4
																											                           FROM RPI_RPBOM_I A, (SELECT * FROM STI_RPCODE_M WHERE /*SCM_FAMILY_CD = 'DRAM' AND*/ NEW_YN = 'Y') M1  --09.02 ★ NAND 별도 수율 적용 관련 TEST
																											                          WHERE A.LINE_CD = 'PKG'
																											                            AND A.USE_YN = 'Y'
																											                            AND A.TO_RP_CD = M1.RP_CD
																									                           ) B
																									                     WHERE A.PLN_REV = V_PLN_REV
																									                       AND A.YLD_GBN_CD = 'PLN'
																									                       AND A.LINE_GRP_CD = 'DIE'
																									                       AND A.YLD > 0 AND A.YLD < 1
																									                       AND A.RP_CD = B.TO_RP_CD
																							                     )
             GROUP BY A.PLN_REV, A.WT_CD, NVL(A.PKG_TYP_CD2, '-'), NVL(A.SCM_PKG_TYP_CD4, '-')
            HAVING SUM(A.WT_OUT_PLN_ADJUST_QTY) >= 1
        )
        -- ★★ 2021.01.13  NAND의 MODE를 RAW NAND로 치환하기 위한 마스터 TABLE
        , NAND_CODE_M AS
        (
            SELECT A.RP_CD AS FR_RP_CD, MAX(B.RP_CD) AS TO_RP_CD
              FROM STI_RPCODE_M A
                 , (
                 			SELECT *
                        FROM STI_RPCODE_M
                    	 WHERE NEW_YN = 'Y'
                         AND LINE_CD = 'WFT'
                         AND SCM_FAMILY_CD = 'NAND'
                         AND CHG_PROD_MODE_CD = 'Raw NAND'
                         AND CHG_BIZ_TYP_CD IS NULL
                         AND FAB_UNUS_OPER_VAL IS NULL
                   ) B
             WHERE A.NEW_YN = 'Y'
               AND A.LINE_CD = 'WFT'
               AND A.SCM_FAMILY_CD = 'NAND'
               AND A.CHG_BIZ_TYP_CD IS NULL
               AND A.FAB_ID = B.FAB_ID
               AND A.TECH_CD = B.TECH_CD
               AND A.FAB_DEN_CD = B.FAB_DEN_CD
               AND A.CELL_LAYER_TYP_CD = B.CELL_LAYER_TYP_CD
               AND A.SCM_PROD_VER_CD = B.SCM_PROD_VER_CD
             GROUP BY A.RP_CD
        )
        -- ★★ 2021.01.13  YLD를 계산하는 중간 서브쿼리 신설
        , WFT_YLD_TBL AS
        (
            SELECT A.PLN_REV, A.LINE_GRP_CD, A.FAB_ID, NVL(F.TO_RP_CD, A.RP_CD) AS RP_CD, A.TGT_YM, '' AS PKG_TYP_CD2
                 , B.SCM_PKG_TYP_CD4 AS SCM_PKG_TYP_CD4  --21.04.14 JHS TSV 코드 구분
                 , NVL(B.CHG_PROD_MODE_CD, '*') AS CHG_PROD_MODE_CD  							--■■■ 로직변경(2023.10)
                 , '' AS PNT_UNUS_OPER_VAL  --21.09.01 JHS POP 및 2406B 구분
                 , MAX(A.YLD * DECODE(B.SCM_FAMILY_CD, 'DRAM',NVL(C.YLD, 1), 'NAND', NVL(D.YLD, 1), 1)) AS YLD
              FROM RPI_YIELD A
                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') B
                 , WFT_DRAM_PORTION C
                 , WFT_FLASH_PORTION D
                 , WFT_NORM_MFG_TBL E
                 , NAND_CODE_M F
             WHERE A.PLN_REV = V_PLN_REV
               AND A.YLD_GBN_CD = 'PLN'
               AND A.LINE_GRP_CD = 'WFT'
               AND A.RP_CD = B.RP_CD
               AND A.RP_CD = C.RP_CD(+)
               AND A.TGT_YM = C.TGT_YM(+)
               AND A.RP_CD = D.RP_CD(+)
               AND A.TGT_YM = D.TGT_YM(+)
               AND A.RP_CD = E.WT_CD
               --■■AND A.TGT_YM BETWEEN E.MIN_TGT_YM AND E.MAX_TGT_YM
               AND A.RP_CD = F.FR_RP_CD(+)
             GROUP BY A.PLN_REV, A.LINE_GRP_CD, A.FAB_ID, NVL(F.TO_RP_CD, A.RP_CD), A.TGT_YM
                    , B.SCM_PKG_TYP_CD4 --21.04.14 JHS TSV 코드 구분
                    , NVL(B.CHG_PROD_MODE_CD, '*')  															--■■■ 로직변경(2023.10)
            HAVING MAX(A.YLD * DECODE(B.SCM_FAMILY_CD, 'DRAM',NVL(C.YLD, 1), 'NAND', NVL(D.YLD, 1), 1)) > 0

            UNION ALL
            -- DIE 수율 반영
            --4가지 Type으로 구분
               --1. SCM_PKG_TYP_CD4 존재 (SCM_PKG_TYP_CD4만 유지)
               --2. PNT_UNUS_OPER_VAL 존재 (PNT_UNUS_OPER_VAL, PKG_TYP_CD2 유지)
               --3. PKG_TYP_CD2 존재 (PKG_TYP_CD2 유지)
               --4. MODE = 'LPDDR4' AND PKG_TYP_CD2 존재 (PNT_UNUS_OPER_VAL = 'POP')
            SELECT A.PLN_REV, 'WFT' AS LINE_GRP_CD, A.FAB_ID, C.WFT_RP_CD AS RP_CD, A.TGT_YM
                 , CASE WHEN B.SCM_PKG_TYP_CD4 IS NOT NULL THEN ''
                        WHEN B.PNT_UNUS_OPER_VAL IS NOT NULL THEN B.PKG_TYP_CD2
                        WHEN B.PNT_UNUS_OPER_VAL IS NULL AND B.CHG_PROD_MODE_CD LIKE '%LPDDR%' THEN ''
                        --WHEN B.SCM_FAMILY_CD = 'NAND' THEN B.CHG_PROD_MODE_CD||' '||B.PKG_TYP_CD2  --22.09.02 ★ NAND 별도 수율 적용 관련 TEST
                   ELSE B.PKG_TYP_CD2 END AS PKG_TYP_CD2  --21.09.01 JHS POP 및 2406B 구분
                 , B.SCM_PKG_TYP_CD4
                 , NVL(B.CHG_PROD_MODE_CD, '*') AS CHG_PROD_MODE_CD  							--■■■ 로직변경(2023.10)
                 , CASE WHEN B.PNT_UNUS_OPER_VAL IS NULL AND B.CHG_PROD_MODE_CD LIKE '%LPDDR%' THEN 'POP'
                  			ELSE B.PNT_UNUS_OPER_VAL END AS PNT_UNUS_OPER_VAL --21.09.01 JHS POP 및 2406B 구분
                 /*, MAX(A.YLD * D.YLD * NVL(E.YLD, 1)) AS YLD */ --★★WFT 수율 반영 삭제
                 , MAX(A.YLD * DECODE(B.SCM_FAMILY_CD, 'DRAM', NVL(E.YLD, 1), 'NAND', NVL(H.YLD, 1), 1)) AS YLD  --22.11.29 JHS NAND 별도 수율 LAD2 적용
              FROM RPI_YIELD A
                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') B
                 , (SELECT PKG_RP_CD, MAX(WFT_RP_CD) AS WFT_RP_CD FROM RPI_RPBOM_TREE_I
                     WHERE PLN_REV = SUBSTR(V_PLN_REV, 1, 13)||'BSE-01'
                       AND CHG_BIZ_TYP_CD = 'C'
                     GROUP BY PKG_RP_CD) C
                 , WFT_DRAM_PORTION E
                 , WFT_SPCL_MFG_TBL F
                 , (
                 			SELECT DISTINCT RP_CD
                   		  FROM RPI_YIELD A
                      		 , RPI_PLN_REV B
                   		 WHERE A.PLN_REV = V_PLN_REV
	                       AND B.PLN_REV = A.PLN_REV
                         AND A.YLD_GBN_CD = 'PLN'
                         AND A.LINE_GRP_CD = 'DIE'
                         AND A.TGT_YM BETWEEN B.PLN_START_YM AND B.PLN_END_YM
                         AND A.YLD > 0 AND A.YLD < 1
                   ) G
                 , WFT_FLASH_PORTION H  --22.11.29 JHS NAND LAD2 PORTION 반영
             WHERE A.PLN_REV = V_PLN_REV
               AND A.YLD_GBN_CD = 'PLN'
               AND A.LINE_GRP_CD = 'DIE'
               AND A.RP_CD = G.RP_CD
               AND A.RP_CD = B.RP_CD
               AND A.RP_CD = C.PKG_RP_CD
               AND C.WFT_RP_CD = E.RP_CD(+)
               AND A.TGT_YM = E.TGT_YM(+)
               AND C.WFT_RP_CD = F.WT_CD
               /* 22.11.29 JHS NAND LAD2 PORTION 반영 */
               AND C.WFT_RP_CD = H.RP_CD(+)
               AND A.TGT_YM = H.TGT_YM(+)
               ----------------------------------------
               --■■AND A.TGT_YM BETWEEN F.MIN_TGT_YM AND F.MAX_TGT_YM
             GROUP BY A.PLN_REV, A.FAB_ID, C.WFT_RP_CD, A.TGT_YM
                 , CASE WHEN B.SCM_PKG_TYP_CD4 IS NOT NULL THEN ''
                        WHEN B.PNT_UNUS_OPER_VAL IS NOT NULL THEN B.PKG_TYP_CD2
                        WHEN B.PNT_UNUS_OPER_VAL IS NULL AND B.CHG_PROD_MODE_CD LIKE '%LPDDR%' THEN ''
                        --WHEN B.SCM_FAMILY_CD = 'NAND' THEN B.CHG_PROD_MODE_CD||' '||B.PKG_TYP_CD2  --22.09.02 ★ NAND 별도 수율 적용 관련 TEST
                        ELSE B.PKG_TYP_CD2
                   END --21.09.01 JHS POP 및 2406B 구분
                 , B.SCM_PKG_TYP_CD4
                 , NVL(B.CHG_PROD_MODE_CD, '*')  															--■■■ 로직변경(2023.10)
                 , CASE WHEN B.PNT_UNUS_OPER_VAL IS NULL AND B.CHG_PROD_MODE_CD LIKE '%LPDDR%' THEN 'POP'
                        ELSE B.PNT_UNUS_OPER_VAL
                   END --21.09.01 JHS POP 및 2406B 구분
        )

				SELECT V_PLN_REV AS PLN_REV, B.SCM_FAMILY_CD, A.FAB_ID, NVL(B.TECH_CD,' '), NVL(B.FAB_DEN_CD,' '), NVL(B.CELL_LAYER_TYP_CD,' ')
             , NVL(A.CHG_PROD_MODE_CD, '*') AS CHG_PROD_MODE_CD  							--■■■ 로직변경(2023.10) , NVL(CASE WHEN B.SCM_FAMILY_CD = 'NAND' THEN 'Raw NAND' ELSE B.CHG_PROD_MODE_CD END,' ') AS CHG_PROD_MODE_CD  --22.09.02 ★ NAND 별도 수율 적용 관련 TEST
             , NVL(B.SCM_PROD_VER_CD,' ')
             , NVL(B.NET_DIE_300_CNT,0), A.LINE_GRP_CD, NVL(A.SCM_PKG_TYP_CD4,' '), NVL(A.PKG_TYP_CD2,' ')
             , NVL(A.PNT_UNUS_OPER_VAL,' ')  --21.09.01 JHS POP 및 2406B 구분
             , B.SCM_FAMILY_CD AS ORG_SCM_FAMILY_CD, A.TGT_YM, V_PLN_YM AS PLN_YM, V_PLN_WEEK_GBN_CD AS PLN_WEEK_GBN_CD
             , A.YLD AS YLD, REPLACE(C.FA2_RP_CD, '_TSV', '') AS FAB2_CD --21.04.14 TSV 제품은 NON_TSV 제품으로 추가
             , '' AS CUM_YLD_APPLY_TGT_YN, 0 AS SORT_SEQ ,SYSDATE AS CRT_TM, 'MFG_YIELD_SP' AS CRT_USER_ID, '' AS CHG_TM, '' AS CHG_USER_ID
          FROM WFT_YLD_TBL A
             , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') B
             , (
             			SELECT WFT_RP_CD, MAX(FA2_RP_CD) AS FA2_RP_CD
             			  FROM RPI_RPBOM_TREE_I
                   WHERE PLN_REV = SUBSTR(V_PLN_REV, 1, 13)||'BSE-01'
                   GROUP BY WFT_RP_CD
               ) C
         WHERE A.RP_CD = B.RP_CD
           AND A.RP_CD = C.WFT_RP_CD(+)
				;

       	COMMIT;
       	DBMS_OUTPUT.PUT_LINE('**********[ p  t YIELD INSERT  MERGE] **********'||'-'|| TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS'));

       	-- 03. P and T YIELD INSERT
        INSERT INTO RPO_MFG_YIELD(
	        							  		  		PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD
	        												, NET_DIE_300_CNT, LINE_GRP_CD, TSV_GBN_CD, PKG_TYP_CD2, PNT_PLN_SPCL_CD
	                                , ORG_SCM_FAMILY_CD, TGT_YM, PLN_YM, PLN_WEEK_GBN_CD, YLD, FAB2_CD, CUM_YLD_APPLY_TGT_YN
	                                , SORT_SEQ, CRT_TM, CRT_USER_ID, CHG_TM, CHG_USER_ID
                                 )
       	WITH WLP_YLD_TBL AS
       	(
        		/* 1.0 TSV를 제외(단품) */
            SELECT A.PLN_REV, A.LINE_GRP_CD, A.FAB_ID, B.FGS_RP_CD AS RP_CD, A.RP_CD AS WLP_RP_CD, A.TGT_YM, A.YLD
              FROM RPI_YIELD A
                 , (
                 			SELECT FGS_RP_CD, WLP_RP_CD FROM RPI_RPBOM_TREE_I
                  		 WHERE PLN_REV = SUBSTR(V_PLN_REV, 1, 13)||'BSE-01'
                         AND CHG_BIZ_TYP_CD = 'C'
                         AND TRIM(WLP_RP_CD) IS NOT NULL
                   ) B
             WHERE PLN_REV = V_PLN_REV
               AND YLD_GBN_CD = 'PLN'
               AND LINE_GRP_CD = 'WLP'
               AND A.RP_CD = B.WLP_RP_CD
       	)
        , TSV_WLP_YLD_TBL AS
        (
        		/* Module 제품에 대한 단품 */
        		SELECT A.PLN_REV, A.LINE_GRP_CD, A.FAB_ID, B.FGS_RP_CD AS RP_CD, A.RP_CD AS WLP_RP_CD, A.TGT_YM, A.YLD
              FROM RPI_YIELD A
                 , (
                 			SELECT DISTINCT A.SUB_RP_CD AS FGS_RP_CD, B.WLP_RP_CD AS WLP_RP_CD, B.CHG_BIZ_TYP_CD
                        FROM STI_RP_CD_SPLIT_VW A
                            , RPI_RPBOM_TREE_I B
                  		 WHERE 1 = 1
                         AND A.RP_CD = B.FGS_RP_CD
                         AND B.PLN_REV = SUBSTR(V_PLN_REV, 1, 13)||'BSE-01'
                         AND TRIM(B.WLP_RP_CD) IS NOT NULL
                       ORDER BY B.WLP_RP_CD
                   ) B
             WHERE A.PLN_REV = V_PLN_REV
               AND YLD_GBN_CD = 'PLN'
               AND LINE_GRP_CD = 'WLP'
               AND A.RP_CD = B.WLP_RP_CD
        )
       	-- 생산량이 없는 경우의 PKG YLD (SUB_RP_CD COUNT = 1만 반영)
       	, PKG_YLD_NO_MFG_TBL AS
       	(
            SELECT PLN_REV, LINE_GRP_CD, RP_CD, ORG_SCM_FAMILY_CD, TGT_YM, YLD
              FROM (
                				SELECT A.PLN_REV, A.LINE_GRP_CD, A.RP_CD AS ORG_RP_CD, NVL(C.RP_CD, B.SUB_RP_CD) AS RP_CD
                        		 , CASE WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.SCM_FAMILY_CD = 'Hybrid' THEN 'Hybrid'
                               			WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.RP_CD LIKE '%BGA%' THEN 'SSD'
                          					ELSE B.SUB_SCM_FAMILY_CD
                               END AS ORG_SCM_FAMILY_CD
                        		 , A.TGT_YM, A.YLD
                        		 , COUNT(*) OVER (PARTITION BY NVL(C.RP_CD, B.SUB_RP_CD), A.TGT_YM
		                                                				 , CASE WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.SCM_FAMILY_CD = 'Hybrid' THEN 'Hybrid'
		                                                       					WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.RP_CD LIKE '%BGA%' THEN 'SSD'
		                                                  							ELSE B.SUB_SCM_FAMILY_CD
		                                                           END) AS CNT
                    		  FROM RPI_YIELD A
                        		 , STI_RP_CD_SPLIT_VW B
                        		 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y' AND NVL(CHG_BIZ_TYP_CD, '-') = 'C' ) C   --PKG -> FGS CODE 변환  --22.04.13 DIMM 반영 현상 조치 (CHG_BIZ_TYP_CD = 'C')
                        	 	 , RPI_PLN_REV D
                    		 WHERE A.PLN_REV = V_PLN_REV
                        	 AND D.PLN_REV = A.PLN_REV
                        	 AND A.LINE_GRP_CD = 'PKG'
                        	 AND A.YLD_GBN_CD = 'PLN'
                           AND A.TGT_YM BETWEEN D.PLN_START_YM AND D.PLN_END_YM
                        	 AND A.RP_CD = B.RP_CD
                        	 AND B.SUB_RP_CD = C.PKG_CD(+)
                	 )
             WHERE CNT = 1
        )
        -- 생산량이 있는 경우의 PKG YLD
        , PKG_YLD_MFG_TBL AS
        (
            SELECT PLN_REV, LINE_GRP_CD, RP_CD, ORG_SCM_FAMILY_CD, TGT_YM
                 , SUM(ORG_QTY_YLD) / SUM(PLN_QTY) AS YLD
              FROM (

				                SELECT A.PLN_REV, C.LINE_GRP_CD, A.RP_CD AS ORG_RP_CD, NVL(E.RP_CD, B.SUB_RP_CD) AS RP_CD
				                     , CASE WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.SCM_FAMILY_CD = 'Hybrid' THEN 'Hybrid'
				                            WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.RP_CD LIKE '%BGA%' THEN 'SSD'
				                       ELSE B.SUB_SCM_FAMILY_CD END AS ORG_SCM_FAMILY_CD
				                     , A.TGT_YM, SUM(A.PLN_DATA_VAL * B.SUB_RP_CNT) AS PLN_QTY, MAX(C.YLD) AS ORG_PKG_YLD
				                     , SUM(A.PLN_DATA_VAL * B.SUB_RP_CNT) * MAX(C.YLD) AS ORG_QTY_YLD
				                  FROM RPO_SITE_LINE_MFG_PLN A
				                     , STI_RP_CD_SPLIT_VW B
				                     , (
                             			SELECT * FROM RPI_YIELD
				                       		 WHERE PLN_REV = V_PLN_REV
				                         		 AND YLD_GBN_CD = 'PLN'
				                         		 AND LINE_GRP_CD = 'PKG'
                               ) C
				                     , RPI_PLN_REV D
				                     , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y' AND NVL(CHG_BIZ_TYP_CD, '-') = 'C') E    --PKG -> FGS CODE 변환  --22.04.13 DIMM 반영 현상 조치 (CHG_BIZ_TYP_CD = 'C')
				                 WHERE A.PLN_REV = V_PLN_REV
				                   AND D.PLN_REV = A.PLN_REV
				                   AND A.LINE_CD = 'PKG'
				                   AND A.PLN_TYP_CD = 'OUT'
				                   AND A.TGT_YM BETWEEN D.PLN_START_YM AND D.PLN_END_YM
				                   AND A.RP_CD = B.RP_CD
				                   AND A.RP_CD = C.RP_CD
				                   AND A.TGT_YM = C.TGT_YM
				                   AND B.SUB_RP_CD = E.PKG_CD(+)
				                 GROUP BY A.PLN_REV, C.LINE_GRP_CD, A.RP_CD, NVL(E.RP_CD, B.SUB_RP_CD)
						                    , CASE WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.SCM_FAMILY_CD = 'Hybrid' THEN 'Hybrid'
						                           WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.RP_CD LIKE '%BGA%' THEN 'SSD'
						                      		 ELSE B.SUB_SCM_FAMILY_CD
                                  END
                                , A.TGT_YM
				                HAVING SUM(A.PLN_DATA_VAL * B.SUB_RP_CNT) >= 1
			            )
             GROUP BY PLN_REV, LINE_GRP_CD, RP_CD, ORG_SCM_FAMILY_CD, TGT_YM
        )
        -- PKG YLD 통합
        , PKG_YLD_TBL AS
        (
            SELECT A.PLN_REV, A.LINE_GRP_CD, A.RP_CD, A.ORG_SCM_FAMILY_CD, A.TGT_YM, A.YLD FROM
                (SELECT * FROM PKG_YLD_MFG_TBL

                UNION ALL

                SELECT * FROM PKG_YLD_NO_MFG_TBL
                WHERE /*RP_CD IN (SELECT DISTINCT RP_CD FROM PKG_YLD_MFG_TBL) -- '21.01.18 JHS 생산 계획이 없는 RP CD도 보이도록 수정
                    AND*/ (RP_CD, ORG_SCM_FAMILY_CD, TGT_YM) NOT IN
                        (SELECT DISTINCT RP_CD, ORG_SCM_FAMILY_CD, TGT_YM FROM PKG_YLD_MFG_TBL)
                ) A
        )
        -- 생산량이 없는 경우의 PKT YLD (SUB_RP_CD COUNT = 1만 반영)
        , PKT_YLD_NO_MFG_TBL AS
        (
        		SELECT PLN_REV, LINE_GRP_CD, RP_CD, ORG_SCM_FAMILY_CD, TGT_YM, YLD
              FROM (
			                SELECT A.PLN_REV, A.LINE_GRP_CD, A.RP_CD AS ORG_RP_CD, NVL(C.RP_CD, B.SUB_RP_CD) AS RP_CD
			                     , CASE WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.SCM_FAMILY_CD = 'Hybrid' THEN 'Hybrid'
			                            WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.RP_CD LIKE '%BGA%' THEN 'SSD'
			                       		  ELSE B.SUB_SCM_FAMILY_CD
                             END AS ORG_SCM_FAMILY_CD
			                     , A.TGT_YM, A.YLD
			                     , COUNT(*) OVER (PARTITION BY NVL(C.RP_CD, B.SUB_RP_CD), A.TGT_YM
			                                                 , CASE WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.SCM_FAMILY_CD = 'Hybrid' THEN 'Hybrid'
			                                                        WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.RP_CD LIKE '%BGA%' THEN 'SSD'
			                                                  			ELSE B.SUB_SCM_FAMILY_CD END) AS CNT
			                  FROM RPI_YIELD A
			                     , STI_RP_CD_SPLIT_VW B
			                     , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y' AND NVL(CHG_BIZ_TYP_CD, '-') = 'C') C  -- PKG -> FGS CODE 변환  --22.04.13 DIMM 반영 현상 조치 (CHG_BIZ_TYP_CD = 'C')
			                     , RPI_PLN_REV D
			                 WHERE A.PLN_REV = V_PLN_REV
			                   AND D.PLN_REV = A.PLN_REV
			                   AND A.LINE_GRP_CD = 'PKT'
			                   AND A.YLD_GBN_CD = 'PLN'
			                   AND A.TGT_YM BETWEEN D.PLN_START_YM AND D.PLN_END_YM
			                   AND A.RP_CD = B.RP_CD
			                   AND B.SUB_RP_CD = C.TEST_CD(+)
                   )
             WHERE CNT = 1
        )
        -- 생산량이 있는 경우의 PKT YLD
        , PKT_YLD_MFG_TBL AS
        (
        		SELECT PLN_REV, LINE_GRP_CD, RP_CD, ORG_SCM_FAMILY_CD, TGT_YM
                 , SUM(ORG_QTY_YLD) / SUM(PLN_QTY) AS YLD
              FROM (
				               SELECT A.PLN_REV, C.LINE_GRP_CD, A.RP_CD AS ORG_RP_CD, NVL(E.RP_CD, B.SUB_RP_CD) AS RP_CD
				                    , CASE WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.SCM_FAMILY_CD = 'Hybrid' THEN 'Hybrid'
				                           WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.RP_CD LIKE '%BGA%' THEN 'SSD'
				                      		 ELSE B.SUB_SCM_FAMILY_CD
                              END AS ORG_SCM_FAMILY_CD
				                    , A.TGT_YM, SUM(A.PLN_DATA_VAL * B.SUB_RP_CNT) AS PLN_QTY, MAX(C.YLD) AS ORG_PKG_YLD
				                    , SUM(A.PLN_DATA_VAL * B.SUB_RP_CNT) * MAX(C.YLD) AS ORG_QTY_YLD
				                 FROM RPO_SITE_LINE_MFG_PLN A
				                    , STI_RP_CD_SPLIT_VW B
				                    , (
                              		SELECT * FROM RPI_YIELD
				                       		 WHERE PLN_REV = V_PLN_REV
				                         		 AND YLD_GBN_CD = 'PLN'
				                         		 AND LINE_GRP_CD = 'PKT'
                               ) C
				                    , RPI_PLN_REV D
				                    , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y' AND NVL(CHG_BIZ_TYP_CD, '-') = 'C') E  --22.04.13 DIMM 반영 현상 조치 (CHG_BIZ_TYP_CD = 'C')
				                WHERE A.PLN_REV = V_PLN_REV
				                  AND D.PLN_REV = A.PLN_REV
				                  AND A.LINE_CD = 'PKC'
				                  AND A.PLN_TYP_CD = 'OUT'
				                  AND A.TGT_YM BETWEEN D.PLN_START_YM AND D.PLN_END_YM
				                  AND A.RP_CD = B.RP_CD
				                  AND A.RP_CD = C.RP_CD
				                  AND A.TGT_YM = C.TGT_YM
				                  AND B.SUB_RP_CD = E.TEST_CD(+)
				                GROUP BY A.PLN_REV, C.LINE_GRP_CD, A.RP_CD, NVL(E.RP_CD, B.SUB_RP_CD)
				                    , CASE WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.SCM_FAMILY_CD = 'Hybrid' THEN 'Hybrid'
				                           WHEN B.SUB_SCM_FAMILY_CD = 'DRAM' AND B.RP_CD LIKE '%BGA%' THEN 'SSD'
				                      		 ELSE B.SUB_SCM_FAMILY_CD
                              END
                            , A.TGT_YM
				                HAVING SUM(A.PLN_DATA_VAL * B.SUB_RP_CNT) >= 1
            			 )
             GROUP BY PLN_REV, LINE_GRP_CD, RP_CD, ORG_SCM_FAMILY_CD, TGT_YM
        )
        -- PKT YLD 통합
        , PKT_YLD_TBL AS
        (
            SELECT A.PLN_REV, A.LINE_GRP_CD, A.RP_CD, A.ORG_SCM_FAMILY_CD, A.TGT_YM, A.YLD
              FROM (
              				SELECT *
                        FROM PKT_YLD_MFG_TBL

                			UNION ALL

                			SELECT *
                        FROM PKT_YLD_NO_MFG_TBL
                			 WHERE 1 = 1/* AND RP_CD IN (SELECT DISTINCT RP_CD FROM PKT_YLD_MFG_TBL)  -- '21.01.18 JHS 생산 계획이 없는 RP CD도 보이도록 수정 */
                         AND (RP_CD, ORG_SCM_FAMILY_CD, TGT_YM) NOT IN (SELECT DISTINCT RP_CD, ORG_SCM_FAMILY_CD, TGT_YM FROM PKT_YLD_MFG_TBL)
                	  ) A
        )
        , PKT_PRTN_TBL AS
        (
            SELECT A.PLN_REV, A.PRTN_TYP_CD, A.LINE_CD, B.RP_CD AS RP_CD, A.RP_CD AS ORG_RP_CD, A.TGT_YM, (1 - A.YLD) AS YLD
              FROM RPI_PORTION A
                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') B
             WHERE A.PLN_REV = V_PLN_REV
               AND A.PRTN_DATA_GBN_CD = 'PLN'
               AND A.LINE_CD = 'PKC'
               AND A.YLD > 0
               AND A.RP_CD = B.TEST_CD
        )
        --PKT 생산
        , PKT_MFG_TBL AS
        (
            SELECT A.PLN_REV, A.LINE_CD
                 , G.FAB_ID, G.TECH_CD, G.FAB_DEN_CD, G.CHG_PROD_MODE_CD, G.CELL_LAYER_TYP_CD, G.SCM_PROD_VER_CD, G.SCM_PKG_TYP_CD4  -- '21.01.18 JHS RP_CD가 아닌 속성 기준으로 제어
                 , MIN(A.TGT_YM) AS MIN_TGT_YM, MAX(A.TGT_YM) AS MAX_TGT_YM
                 , REPLACE(NVL(TRIM(D.FA2_RP_CD), F.FAB2_CD), '_TSV', '') AS FA2_CD  --21.04.14 JHS TSV는 NON_TSV로 삽입
                 , NVL(E.NET_DIE_300_CNT, F.NET_DIE_300_CNT) AS NET_DIE_300_CNT
                 , SUM(PLN_DATA_VAL) AS PLN_QTY
              FROM RPO_LINE_MFG_PLN_MG_VW A
                 , RPI_PLN_REV B
                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') C  --FGS_CD SEARCH
                 , (SELECT FGS_RP_CD, MAX(WFT_RP_CD) AS WFT_RP_CD, MAX(FA2_RP_CD) AS FA2_RP_CD FROM RPI_RPBOM_TREE_I
                     WHERE PLN_REV = SUBSTR(V_PLN_REV, 1, 13)||'BSE-01'
                       AND CHG_BIZ_TYP_CD = 'C'
                       AND WFT_RP_CD NOT LIKE '%BASE%'
                       AND FA2_RP_CD NOT LIKE '%BASE%'
                     GROUP BY FGS_RP_CD) D
                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') E  --NET_DIE
                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') F  --FAB2_CD, NET_DIE B/U
                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') G  --'21.01.18 JHS FGS CD에 대한 속성 SEARCH
             WHERE A.PLN_REV = V_PLN_REV
               AND B.PLN_REV = A.PLN_REV
               AND A.LINE_CD = 'PKC'
               AND A.PLN_TYP_CD = 'OUT'
               AND A.TGT_YM BETWEEN B.PLN_START_YM AND B.PLN_END_YM
               AND NVL(C.CHG_BIZ_TYP_CD, '-') <> 'NK'  --21.04.14 JHS NK CODE 제외 추가
               AND A.RP_CD = C.TEST_CD(+)
               AND NVL(C.RP_CD, A.RP_CD) = D.FGS_RP_CD (+)
               AND D.WFT_RP_CD = E.RP_CD (+)
               AND NVL(C.RP_CD, A.RP_CD) = F.RP_CD
               AND NVL(C.RP_CD, A.RP_CD) = G.RP_CD   --'21.01.18 JHS
             GROUP BY A.PLN_REV, A.LINE_CD
                 , G.FAB_ID, G.TECH_CD, G.FAB_DEN_CD, G.CHG_PROD_MODE_CD, G.CELL_LAYER_TYP_CD, G.SCM_PROD_VER_CD, G.SCM_PKG_TYP_CD4 --'21.01.18 JHS
                 , NVL(TRIM(D.FA2_RP_CD), F.FAB2_CD), NVL(E.NET_DIE_300_CNT, F.NET_DIE_300_CNT)
        )
        SELECT PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD, NET_DIE_300_CNT, LINE_GRP_CD, TSV_GBN_CD, PKG_TYP_CD2
        		 , PNT_PLN_SPCL_CD, ORG_SCM_FAMILY_CD, TGT_YM, PLN_YM, PLN_WEEK_GBN_CD, YLD, FAB2_CD, CUM_YLD_APPLY_TGT_YN, SORT_SEQ, CRT_TM, CRT_USER_ID, CHG_TM, CHG_USER_ID
          FROM (
          			  /* 아래 TSV(Module) 제품과 분리하여 수율계산하도록 변경함(2023.11.21)
          				SELECT V_PLN_REV AS PLN_REV, F.SCM_FAMILY_CD, F.FAB_ID,  NVL(F.TECH_CD,' ') AS TECH_CD, NVL(F.FAB_DEN_CD,' ') AS FAB_DEN_CD
			                 , NVL(F.CELL_LAYER_TYP_CD,' ') AS CELL_LAYER_TYP_CD, NVL(F.CHG_PROD_MODE_CD,' ') AS CHG_PROD_MODE_CD
			                 , NVL(F.SCM_PROD_VER_CD,' ') AS SCM_PROD_VER_CD, E.NET_DIE_300_CNT
			                 , 'P_T' AS LINE_GRP_CD, NVL(NVL(F.TSV_GBN_CD, F.SCM_PKG_TYP_CD4), ' ') AS TSV_GBN_CD, NVL(F.PKG_TYP_CD2,' ') AS PKG_TYP_CD2
			                 , NVL(F.PNT_UNUS_OPER_VAL,' ') AS PNT_PLN_SPCL_CD, A.ORG_SCM_FAMILY_CD, A.TGT_YM, V_PLN_YM AS PLN_YM, V_PLN_WEEK_GBN_CD AS PLN_WEEK_GBN_CD
			                 , (A.YLD * B.YLD * NVL(C.YLD, 1) * NVL(D.YLD, 1)) AS YLD
			                 , NVL(E.FA2_CD, ' ') AS FAB2_CD, 'N' AS CUM_YLD_APPLY_TGT_YN, 0 AS SORT_SEQ ,SYSDATE AS CRT_TM, 'MFG_YIELD_SP' AS CRT_USER_ID
			                 , '' AS CHG_TM, '' AS CHG_USER_ID
			              FROM PKT_YLD_TBL A
			                 , PKG_YLD_TBL B
			                 , WLP_YLD_TBL C
			                 , PKT_PRTN_TBL D
			                 , PKT_MFG_TBL E
			                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y' AND TRIM(FAB_UNUS_OPER_VAL) IS NULL) F
			             WHERE A.RP_CD = B.RP_CD
			               AND A.ORG_SCM_FAMILY_CD = B.ORG_SCM_FAMILY_CD
			               AND A.TGT_YM = B.TGT_YM
			               AND A.RP_CD = C.RP_CD(+)
			               AND A.TGT_YM = C.TGT_YM(+)
			               AND A.RP_CD = D.RP_CD(+)
			               AND A.TGT_YM = D.TGT_YM(+)
			               --AND A.RP_CD = E.RP_CD
			               --AND A.ORG_SCM_FAMILY_CD = E.ORG_SCM_FAMILY_CD  --'21.01.18 JHS 속성 기준으로 제어
			               AND A.RP_CD = F.RP_CD
			               AND F.FAB_ID = E.FAB_ID  --'21.01.18 JHS
			               AND F.TECH_CD = E.TECH_CD  --'21.01.18 JHS
			               AND F.FAB_DEN_CD = E.FAB_DEN_CD  --'21.01.18 JHS
			               AND F.CHG_PROD_MODE_CD = E.CHG_PROD_MODE_CD  --'21.01.18 JHS
			               AND NVL(F.CELL_LAYER_TYP_CD, '*') = NVL(E.CELL_LAYER_TYP_CD, '*')  --'21.01.18 JHS
			               AND NVL(F.SCM_PROD_VER_CD, '*') = NVL(E.SCM_PROD_VER_CD, '*')  --'21.01.18 JHS
			               AND NVL(F.SCM_PKG_TYP_CD4, '*') = NVL(E.SCM_PKG_TYP_CD4, '*')  --'21.01.18 JHS
			               AND A.TGT_YM BETWEEN E.MIN_TGT_YM AND E.MAX_TGT_YM
                  */

                  /* ====================================================================== */
                  -- TSV가 아닌 제품
                  SELECT DISTINCT V_PLN_REV AS PLN_REV, F.SCM_FAMILY_CD, F.FAB_ID,  NVL(F.TECH_CD,' ') AS TECH_CD, NVL(F.FAB_DEN_CD,' ') AS FAB_DEN_CD
			                 , NVL(F.CELL_LAYER_TYP_CD,' ') AS CELL_LAYER_TYP_CD, NVL(F.CHG_PROD_MODE_CD,' ') AS CHG_PROD_MODE_CD
			                 , NVL(F.SCM_PROD_VER_CD,' ') AS SCM_PROD_VER_CD, E.NET_DIE_300_CNT
			                 , 'P_T' AS LINE_GRP_CD, NVL(NVL(F.TSV_GBN_CD, F.SCM_PKG_TYP_CD4), ' ') AS TSV_GBN_CD, NVL(F.PKG_TYP_CD2,' ') AS PKG_TYP_CD2
			                 , NVL(F.PNT_UNUS_OPER_VAL,' ') AS PNT_PLN_SPCL_CD, A.ORG_SCM_FAMILY_CD, A.TGT_YM, V_PLN_YM AS PLN_YM, V_PLN_WEEK_GBN_CD AS PLN_WEEK_GBN_CD
			                 , (A.YLD * B.YLD * NVL(C.YLD, 1) * NVL(D.YLD, 1)) AS YLD
			                 , NVL(E.FA2_CD, ' ') AS FAB2_CD, 'N' AS CUM_YLD_APPLY_TGT_YN, 0 AS SORT_SEQ ,SYSDATE AS CRT_TM, 'MFG_YIELD_SP' AS CRT_USER_ID
			                 , '' AS CHG_TM, '' AS CHG_USER_ID
			              FROM PKT_YLD_TBL A
			                 , PKG_YLD_TBL B
			                 , WLP_YLD_TBL C						--■ 단품
			                 , PKT_PRTN_TBL D
			                 , PKT_MFG_TBL E
			                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y' AND TRIM(FAB_UNUS_OPER_VAL) IS NULL) F
			             WHERE A.RP_CD = B.RP_CD
			               AND A.ORG_SCM_FAMILY_CD = B.ORG_SCM_FAMILY_CD
			               AND A.TGT_YM = B.TGT_YM
			               AND A.RP_CD = C.RP_CD (+)
			               AND A.TGT_YM = C.TGT_YM(+)
			               AND A.RP_CD = D.RP_CD(+)
			               AND A.TGT_YM = D.TGT_YM(+)
			               --AND A.RP_CD = E.RP_CD
			               --AND A.ORG_SCM_FAMILY_CD = E.ORG_SCM_FAMILY_CD   --'21.01.18 JHS 속성 기준으로 제어
			               AND A.RP_CD = F.RP_CD
			               AND F.FAB_ID = E.FAB_ID  --'21.01.18 JHS
			               AND F.TECH_CD = E.TECH_CD  --'21.01.18 JHS
			               AND F.FAB_DEN_CD = E.FAB_DEN_CD  --'21.01.18 JHS
			               AND F.CHG_PROD_MODE_CD = E.CHG_PROD_MODE_CD  --'21.01.18 JHS
			               AND NVL(F.CELL_LAYER_TYP_CD, '*') = NVL(E.CELL_LAYER_TYP_CD, '*')  --'21.01.18 JHS
			               AND NVL(F.SCM_PROD_VER_CD, '*') = NVL(E.SCM_PROD_VER_CD, '*')  --'21.01.18 JHS
			               AND NVL(F.SCM_PKG_TYP_CD4, '*') = NVL(E.SCM_PKG_TYP_CD4, '*')  --'21.01.18 JHS
			               AND A.TGT_YM BETWEEN E.MIN_TGT_YM AND E.MAX_TGT_YM
										 AND NVL(NVL(F.TSV_GBN_CD, F.SCM_PKG_TYP_CD4), ' ') != 'TSV'    --WLP 수율값 구할때 TSV는 복함 제품코드

                     UNION ALL

									-- TSV - Module
          				SELECT DISTINCT V_PLN_REV AS PLN_REV, F.SCM_FAMILY_CD, F.FAB_ID,  NVL(F.TECH_CD,' ') AS TECH_CD, NVL(F.FAB_DEN_CD,' ') AS FAB_DEN_CD
			                 , NVL(F.CELL_LAYER_TYP_CD,' ') AS CELL_LAYER_TYP_CD, NVL(F.CHG_PROD_MODE_CD,' ') AS CHG_PROD_MODE_CD
			                 , NVL(F.SCM_PROD_VER_CD,' ') AS SCM_PROD_VER_CD, E.NET_DIE_300_CNT
			                 , 'P_T' AS LINE_GRP_CD, NVL(NVL(F.TSV_GBN_CD, F.SCM_PKG_TYP_CD4), ' ') AS TSV_GBN_CD, NVL(F.PKG_TYP_CD2,' ') AS PKG_TYP_CD2
			                 , NVL(F.PNT_UNUS_OPER_VAL,' ') AS PNT_PLN_SPCL_CD, A.ORG_SCM_FAMILY_CD, A.TGT_YM, V_PLN_YM AS PLN_YM, V_PLN_WEEK_GBN_CD AS PLN_WEEK_GBN_CD
			                 , (A.YLD * B.YLD * NVL(C.YLD, 1) * NVL(D.YLD, 1)) AS YLD
			                 , NVL(E.FA2_CD, ' ') AS FAB2_CD, 'N' AS CUM_YLD_APPLY_TGT_YN, 0 AS SORT_SEQ ,SYSDATE AS CRT_TM, 'MFG_YIELD_SP' AS CRT_USER_ID
			                 , '' AS CHG_TM, '' AS CHG_USER_ID
			              FROM PKT_YLD_TBL A
			                 , PKG_YLD_TBL B
			                 , TSV_WLP_YLD_TBL C		--■ 모듈변환
			                 , PKT_PRTN_TBL D
			                 , PKT_MFG_TBL E
			                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y' AND TRIM(FAB_UNUS_OPER_VAL) IS NULL) F
			             WHERE A.RP_CD = B.RP_CD
			               AND A.ORG_SCM_FAMILY_CD = B.ORG_SCM_FAMILY_CD
			               AND A.TGT_YM = B.TGT_YM
			               AND A.RP_CD = C.RP_CD (+)
			               AND A.TGT_YM = C.TGT_YM(+)
			               AND A.RP_CD = D.RP_CD(+)
			               AND A.TGT_YM = D.TGT_YM(+)
                     --AND A.RP_CD = E.RP_CD
			               --AND A.ORG_SCM_FAMILY_CD = E.ORG_SCM_FAMILY_CD  --'21.01.18 JHS 속성 기준으로 제어
			               AND A.RP_CD = F.RP_CD
			               AND F.FAB_ID = E.FAB_ID  --'21.01.18 JHS
			               AND F.TECH_CD = E.TECH_CD  --'21.01.18 JHS
			               AND F.FAB_DEN_CD = E.FAB_DEN_CD  --'21.01.18 JHS
			               AND F.CHG_PROD_MODE_CD = E.CHG_PROD_MODE_CD  --'21.01.18 JHS
			               AND NVL(F.CELL_LAYER_TYP_CD, '*') = NVL(E.CELL_LAYER_TYP_CD, '*')  --'21.01.18 JHS
			               AND NVL(F.SCM_PROD_VER_CD, '*') = NVL(E.SCM_PROD_VER_CD, '*')  --'21.01.18 JHS
			               AND NVL(F.SCM_PKG_TYP_CD4, '*') = NVL(E.SCM_PKG_TYP_CD4, '*')  --'21.01.18 JHS
			               AND A.TGT_YM BETWEEN E.MIN_TGT_YM AND E.MAX_TGT_YM
										 AND NVL(NVL(F.TSV_GBN_CD, F.SCM_PKG_TYP_CD4), ' ') = 'TSV'			--WLP 수율값 구할때 TSV는 복함 제품코드
                  /* ====================================================================== */
			         )
         GROUP BY PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD, NET_DIE_300_CNT, LINE_GRP_CD, TSV_GBN_CD, PKG_TYP_CD2
                , PNT_PLN_SPCL_CD, ORG_SCM_FAMILY_CD, TGT_YM, PLN_YM, PLN_WEEK_GBN_CD, YLD, FAB2_CD, CUM_YLD_APPLY_TGT_YN, SORT_SEQ, CRT_TM, CRT_USER_ID, CHG_TM, CHG_USER_ID
        ;

        COMMIT;

        -- GHBM P and T YIELD INSERT
        DBMS_OUTPUT.PUT_LINE('**********[ GHBM P and T INSERT  ] **********'||'-'|| TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS'));
        INSERT INTO RPO_MFG_YIELD(
	        							  		  		PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD
	        												, NET_DIE_300_CNT, LINE_GRP_CD, TSV_GBN_CD, PKG_TYP_CD2, PNT_PLN_SPCL_CD
	                                , ORG_SCM_FAMILY_CD, TGT_YM, PLN_YM, PLN_WEEK_GBN_CD, YLD, FAB2_CD, CUM_YLD_APPLY_TGT_YN
	                                , SORT_SEQ, CRT_TM, CRT_USER_ID, CHG_TM, CHG_USER_ID
                                 )
        WITH WLP_MFG_TBL AS
        (
        		SELECT A.PLN_REV, A.LINE_CD/*, A.RP_CD*/
                 , C.SCM_FAMILY_CD, C.FAB_ID, C.TECH_CD, C.FAB_DEN_CD, C.CHG_PROD_MODE_CD, C.SCM_PROD_VER_CD --'21.01.18 JHS 속성 기준으로 제어
                 , MIN(A.TGT_YM) AS MIN_TGT_YM, MAX(A.TGT_YM) AS MAX_TGT_YM, SUM(PLN_DATA_VAL) AS PLN_QTY
              FROM RPO_SITE_LINE_MFG_PLN A
                 , RPI_PLN_REV B
                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') C
             WHERE A.PLN_REV = V_PLN_REV
               AND B.PLN_REV = A.PLN_REV
               AND A.LINE_CD = 'WLP'
               AND A.PLN_TYP_CD = 'OUT'
               AND A.RP_CD LIKE '%HBM%'
               AND A.TGT_YM BETWEEN B.PLN_START_YM AND B.PLN_END_YM
               AND A.RP_CD = C.RP_CD
             GROUP BY A.PLN_REV, A.LINE_CD/*, A.RP_CD*/
                 , C.SCM_FAMILY_CD, C.FAB_ID, C.TECH_CD, C.FAB_DEN_CD, C.CHG_PROD_MODE_CD, C.SCM_PROD_VER_CD --'21.01.18 JHS 속성 기준으로 제어
            HAVING SUM(PLN_DATA_VAL) >= 1
        )
        , P_T_CUM_ORG_TBL AS
        (
        		SELECT A.PLN_REV, A.LINE_GRP_CD, A.FAB_ID, NVL(B.FGS_RP_CD, A.RP_CD) AS RP_CD, A.TGT_YM, A.YLD, B.FA2_RP_CD AS FA2_CD, D.NET_DIE_300_CNT
              FROM RPI_YIELD A
                 , (
                 			SELECT * FROM RPI_RPBOM_TREE_I
                     	 WHERE PLN_REV = SUBSTR(V_PLN_REV, 1, 13)||'BSE-01'
                         AND WLP_RP_CD LIKE '%HBM%'
                         AND FA2_RP_CD NOT LIKE '%BASE%'
                   ) B
                 , WLP_MFG_TBL C
                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') D
                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') E  --'21.01.18 JHS RP CD에 대한 속성 MAPPING
             WHERE A.PLN_REV = V_PLN_REV
               AND A.YLD_GBN_CD = 'PLN'
               AND A.LINE_GRP_CD = 'WLP'
               AND A.RP_CD LIKE '%HBM%'
               AND A.RP_CD = B.WLP_RP_CD
               AND A.RP_CD = E.RP_CD  --'21.01.18
               /*AND A.RP_CD = C.RP_CD*/ --'21.01.18 JHS RP CD가 아닌 속성 기준으로 MAPPING
               AND E.FAB_ID = C.FAB_ID  --'21.01.18 JHS
               AND E.TECH_CD = C.TECH_CD  --'21.01.18 JHS
               AND E.FAB_DEN_CD = C.FAB_DEN_CD  --'21.01.18 JHS
               AND E.CHG_PROD_MODE_CD = C.CHG_PROD_MODE_CD  --'21.01.18 JHS
               AND E.SCM_PROD_VER_CD = E.SCM_PROD_VER_CD  --'21.01.18 JHS
               AND A.TGT_YM BETWEEN C.MIN_TGT_YM AND C.MAX_TGT_YM
               AND B.WFT_RP_CD = D.RP_CD
        )
        SELECT A.PLN_REV, B.SCM_FAMILY_CD, A.FAB_ID, NVL(C.TECH_CD, NVL(B.TECH_CD, ' ')) AS TECH_CD  --0G 제품 FGS제품과 CORE TECH 상이하여 수정
             , NVL(B.FAB_DEN_CD, ' ') AS FAB_DEN_CD
             , NVL(B.CELL_LAYER_TYP_CD, ' ') AS CELL_LAYER_TYP_CD, NVL(B.CHG_PROD_MODE_CD, ' ') AS CHG_PROD_MODE_CD
             , NVL(B.SCM_PROD_VER_CD, ' '), A.NET_DIE_300_CNT, 'P_T' AS LINE_GRP_CD, NVL(B.SCM_PKG_TYP_CD4, ' ') AS TSV_GBN_CD  --21.04.06 실적과의 단차 개선을 위한 수정
             , NVL(B.PKG_TYP_CD2, ' ') AS PKG_TYP_CD2, NVL(B.PNT_UNUS_OPER_VAL, ' ') AS PNT_PLN_SPCL_CD
             , B.SCM_FAMILY_CD AS ORG_SCM_FAMILY_CD, A.TGT_YM, V_PLN_YM AS PLN_YM, V_PLN_WEEK_GBN_CD AS PLN_WEEK_GBN_CD, A.YLD, A.FA2_CD AS FAB2_CD
             , 'N' AS CUM_YLD_APPLY_TGT_YN
             , 0 AS SORT_SEQ, SYSDATE AS CRT_TM, 'MFG_YIELD_SP' AS CRT_USER_ID, '' AS CHG_TM, '' AS CHG_USER_ID
          FROM P_T_CUM_ORG_TBL A
             , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') B
             , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') C
         WHERE A.RP_CD = B.RP_CD
           AND A.FA2_CD = C.RP_CD
        ;

        COMMIT;

        /*  P&T 에 CUM_YLD_APPLY_TGT_YN  설정 추가.   */
        DBMS_OUTPUT.PUT_LINE('**********[ pt Bef Release CUM_YLD_APPLY_TGT_YN update  ] **********'||'-'|| TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS'));
        MERGE INTO RPO_MFG_YIELD A
        USING(
                   SELECT PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD
                   			, NET_DIE_300_CNT, LINE_GRP_CD, TSV_GBN_CD, PKG_TYP_CD2, PNT_PLN_SPCL_CD
                        , ORG_SCM_FAMILY_CD
                     FROM RPO_MFG_YIELD
                    WHERE PLN_REV = V_BEF_PLN_REV
                      AND LINE_GRP_CD = 'P_T'
                      AND CUM_YLD_APPLY_TGT_YN = 'Y'
                    GROUP BY PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD
                    		, NET_DIE_300_CNT, LINE_GRP_CD, TSV_GBN_CD, PKG_TYP_CD2, PNT_PLN_SPCL_CD
                        , ORG_SCM_FAMILY_CD
                    --ORDER BY  FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, PROD_MODE_CD, PLN_PROD_VER_CD

           ) B
        ON (
                       A.PLN_REV = V_PLN_REV
                   AND A.SCM_FAMILY_CD = B.SCM_FAMILY_CD
                   AND A.FAB_ID = B.FAB_ID
                   AND NVL(A.TECH_CD,'*') = NVL(B.TECH_CD,'*')
                   AND NVL(A.FAB_DEN_CD,'*') = NVL(B.FAB_DEN_CD,'*')
                   AND NVL(A.CELL_LAYER_TYP_CD,'*') = NVL(B.CELL_LAYER_TYP_CD,'*')
                   AND NVL(A.CHG_PROD_MODE_CD,'*') = NVL(B.CHG_PROD_MODE_CD,'*')
                   AND NVL(A.SCM_PROD_VER_CD,'*') = NVL(B.SCM_PROD_VER_CD,'*')
                   AND NVL(A.NET_DIE_300_CNT,0) = NVL(B.NET_DIE_300_CNT,0)
                   AND NVL(A.LINE_GRP_CD,'*') = NVL(B.LINE_GRP_CD,'*')
                   AND NVL(A.TSV_GBN_CD,'*') = NVL(B.TSV_GBN_CD,'*')
                   AND NVL(A.PKG_TYP_CD2,'*') = NVL(B.PKG_TYP_CD2,'*')
                   AND NVL(A.PNT_PLN_SPCL_CD,'*') = NVL(B.PNT_PLN_SPCL_CD,'*')
                   AND NVL(A.ORG_SCM_FAMILY_CD,'*') = NVL(B.ORG_SCM_FAMILY_CD,'*')
           )
        WHEN MATCHED THEN
              UPDATE SET A.CUM_YLD_APPLY_TGT_YN = 'Y'
                        ,A.CHG_TM = SYSDATE
                        ,A.CHG_USER_ID = 'BFR_APPLY_YN'
        ;

       	/*  P&T 에 새로운코드(기존release버젼에없는) CUM_YLD_APPLY_TGT_YN  설정 추가.   */
        DBMS_OUTPUT.PUT_LINE('**********[ pt New CUM_YLD_APPLY_TGT_YN update  ] **********'||'-'|| TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS'));

        MERGE INTO RPO_MFG_YIELD A
        USING(
                   SELECT A.PLN_REV, B.SCM_FAMILY_CD, A.FAB_ID, C.TECH_CD /*21.04.14 JHS*/, B.FAB_DEN_CD, B.CELL_LAYER_TYP_CD, B.CHG_PROD_MODE_CD
                        , B.SCM_PROD_VER_CD, 'P_T' AS LINE_GRP_CD
                        , B.SCM_PKG_TYP_CD4 AS TSV_GBN_CD  --'21.04.14 HBM 변경 관련 기인
                        , B.PKG_TYP_CD2, B.PNT_UNUS_OPER_VAL AS PNT_PLN_SPCL_CD, A.ORG_SCM_FAMILY_CD, A.FAB2_CD
                     FROM (
		                        	 SELECT A.PLN_REV, A.LINE_CD, A.FAB_ID, A.RP_CD
				                            , CASE WHEN A.SCM_FAMILY_CD = 'DRAM' AND A.ORG_SCM_FAMILY_CD = 'Hybrid' THEN 'Hybrid'
				                                   WHEN A.SCM_FAMILY_CD = 'DRAM' AND A.ORG_RP_CD LIKE '%BGA%' THEN 'SSD'
				                              ELSE A.SCM_FAMILY_CD END AS ORG_SCM_FAMILY_CD
				                            , REPLACE(NVL(C.FA2_RP_CD, E.FAB2_CD), '_TSV', '') AS FAB2_CD, SUM(A.PLN_DATA_VAL) AS PLN_QTY
				                            , RANK() OVER (PARTITION BY REPLACE(NVL(C.FA2_RP_CD, E.FAB2_CD), '_TSV', '') ORDER BY NVL(SUM(A.PLN_DATA_VAL), 0) DESC) AS RNK  --21.04.14
				                        FROM RPO_LINE_MFG_PLN_MG_VW A
				                            , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') B    -- FGS CODE 속성 MAPPING
				                            , (SELECT * FROM RPI_RPBOM_TREE_I
				                               WHERE PLN_REV = SUBSTR(V_PLN_REV, 1, 13)||'BSE-01'
				                                    AND FA2_RP_CD NOT LIKE '%BASE%') C    -- FGS CD -> FA2 CD MAPPING 및 속성 관리 21.04.14
				                            , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') E   --FGS CD -> FAB2 CD MAPPING2  21.04.14
				                            , RPI_PLN_REV D
				                        WHERE A.PLN_REV = V_PLN_REV
				                          AND D.PLN_REV = A.PLN_REV
				                          AND A.LINE_CD = 'FGS'
				                          AND A.PLN_TYP_CD = 'IN'
				                          AND A.TGT_YM BETWEEN D.PLN_START_YM AND D.PLN_END_YM
				                          --AND A.RP_CD = B.TEST_CD(+)  21.04.14 JHS
				                          AND A.RP_CD = B.RP_CD   --21.04.14 JHS
				                          AND NVL(B.CHG_BIZ_TYP_CD, '-') NOT IN ('NK', 'LAD1', 'LAD2', 'LPGD', 'W')   --21.04.14 JHS
				                          AND A.RP_CD = C.FGS_RP_CD(+)  --21.04.14 JHS
				                          AND A.RP_CD = E.RP_CD
				                            --AND C.CHG_BIZ_TYP_CD NOT IN ('NK', 'LAD1', 'LAD2', 'LPGD', 'W')  --21.04.14 JHS
				                        GROUP BY A.PLN_REV, A.LINE_CD, A.FAB_ID, A.RP_CD, NVL(C.FA2_RP_CD, E.FAB2_CD)
				                            , CASE WHEN A.SCM_FAMILY_CD = 'DRAM' AND A.ORG_SCM_FAMILY_CD = 'Hybrid' THEN 'Hybrid'
				                                   WHEN A.SCM_FAMILY_CD = 'DRAM' AND A.ORG_RP_CD LIKE '%BGA%' THEN 'SSD'
				                              ELSE A.SCM_FAMILY_CD END
                          ) A
                        , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') B
                        , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN = 'Y') C  --21.04.14 JHS 0G 제품 CODE 상이하여 TECH는 FAB2 CD로 변경
                    WHERE A.RP_CD = B.RP_CD
                        AND A.FAB2_CD = C.RP_CD
                        AND A.RNK = 1
                        AND A.FAB2_CD NOT IN (
	                        											SELECT DISTINCT FAB2_CD
	                          											FROM RPO_MFG_YIELD
	                             									 WHERE PLN_REV = V_PLN_REV
	                                								 AND CUM_YLD_APPLY_TGT_YN = 'Y'
                                              )
           ) B
        ON (
                       A.PLN_REV = V_PLN_REV  --21.04.14 JHS 프로시져 속도
                   AND A.SCM_FAMILY_CD = B.SCM_FAMILY_CD
                   AND A.FAB_ID = B.FAB_ID
                   AND NVL(A.TECH_CD,'*') = NVL(B.TECH_CD,'*')
                   AND NVL(A.FAB_DEN_CD,'*') = NVL(B.FAB_DEN_CD,'*')
                   AND NVL(TRIM(A.CELL_LAYER_TYP_CD),'*') = NVL(TRIM(B.CELL_LAYER_TYP_CD),'*')
                   AND NVL(A.CHG_PROD_MODE_CD,'*') = NVL(B.CHG_PROD_MODE_CD,'*')
                   AND NVL(A.SCM_PROD_VER_CD,'*') = NVL(B.SCM_PROD_VER_CD,'*')
                   --AND NVL(A.NET_DIE_300_CNT,0) = NVL(B.NET_DIE_300_CNT,0)
                   AND NVL(A.LINE_GRP_CD,'*') = NVL(B.LINE_GRP_CD,'*')
                   AND NVL(TRIM(A.TSV_GBN_CD),'*') = NVL(TRIM(B.TSV_GBN_CD),'*')
                   AND NVL(A.PKG_TYP_CD2,'*') = NVL(B.PKG_TYP_CD2,'*')
                   AND NVL(TRIM(A.PNT_PLN_SPCL_CD),'*') = NVL(TRIM(B.PNT_PLN_SPCL_CD),'*')
                   AND NVL(A.ORG_SCM_FAMILY_CD,'*') = NVL(B.ORG_SCM_FAMILY_CD,'*')
        	 )
        WHEN MATCHED THEN
              UPDATE SET A.CUM_YLD_APPLY_TGT_YN = 'Y'
                       , A.CHG_TM = SYSDATE
                       , A.CHG_USER_ID = 'NEW_APPLY_YN'
        ;
        COMMIT;
   	END IF;
    -- #######################################################################################################################################################################################

   	IF V_CUM_GUBUN = 'Y' THEN
   			DBMS_OUTPUT.PUT_LINE('**********[ CUM YIELD DELETE  ] **********'||'-'|| TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS'));
				/*
        DELETE FROM RPO_MFG_YIELD
         WHERE PLN_REV = V_PLN_REV
           AND LINE_GRP_CD IN ('CUM1','CUM2','PT_CUM')
      		 --AND CHG_PROD_MODE_CD NOT LIKE '%HBM%'
           AND NVL(FAB2_CD,'*') NOT IN ('FMY_AVG', 'FAB_AVG')
        ;
        SELECT * FROM RPO_MFG_YIELD
        */
        --DRAM
        DELETE FROM RPO_MFG_YIELD
         WHERE PLN_REV = V_PLN_REV
           AND SCM_FAMILY_CD = 'DRAM'
           AND LINE_GRP_CD IN ('CUM1','CUM2','PT_CUM')
      		 --AND CHG_PROD_MODE_CD NOT LIKE '%HBM%'
           AND NVL(FAB2_CD,'*') NOT IN ('FMY_AVG', 'FAB_AVG')
        ;

        --NAND
        DELETE FROM RPO_MFG_YIELD
         WHERE PLN_REV = V_PLN_REV
           AND SCM_FAMILY_CD = 'NAND'
           AND CHG_PROD_MODE_CD = 'Total'
           --■■■ 로직변경(2023.10)
           --AND LINE_GRP_CD IN ('CUM1','CUM2','PT_CUM')
           AND LINE_GRP_CD IN ('WFT', 'CUM1','CUM2','PT_CUM')
      		 --AND CHG_PROD_MODE_CD NOT LIKE '%HBM%'
           AND NVL(FAB2_CD,'*') NOT IN ('FMY_AVG', 'FAB_AVG')
        ;
   	END IF;

		COMMIT;

    -- ==========================================================================================================================================================
    -- 7-1.NAND - TOTAL(WFT, PT_CUM) 생성
		DBMS_OUTPUT.PUT_LINE('07-1. NAND - TOTAL(WFT, PT_CUM) Insert');
    INSERT INTO RPO_MFG_YIELD(PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD
    													, CHG_PROD_MODE_CD
                              , SCM_PROD_VER_CD, NET_DIE_300_CNT, LINE_GRP_CD, TSV_GBN_CD, PKG_TYP_CD2, PNT_PLN_SPCL_CD
    											  	, ORG_SCM_FAMILY_CD, TGT_YM, PLN_YM, PLN_WEEK_GBN_CD, YLD, FAB2_CD
                              , CUM_YLD_APPLY_TGT_YN, SORT_SEQ
                            	, CRT_TM, CRT_USER_ID, CHG_TM, CHG_USER_ID
                             )
    -- WFT 생성(Total)
    SELECT A.PLN_REV, A.SCM_FAMILY_CD, A.FAB_ID, A.TECH_CD, A.FAB_DEN_CD, A.CELL_LAYER_TYP_CD
         , 'Total' AS CHG_PROD_MODE_CD
		     , A.SCM_PROD_VER_CD, A.NET_DIE_300_CNT, 'WFT' AS LINE_GRP_CD, A.TSV_GBN_CD, A.PKG_TYP_CD2, A.PNT_PLN_SPCL_CD
         , A.ORG_SCM_FAMILY_CD, A.TGT_YM, A.PLN_YM, A.PLN_WEEK_GBN_CD, A.YLD, A.FAB2_CD
		     , 'N' AS CUM_YLD_APPLY_TGT_YN, A.SORT_SEQ
         , SYSDATE, 'MFG_YIELD_SP(TOTAL)', '' AS CHG_TM, '' AS CHG_USER_ID
      FROM RPO_MFG_YIELD A
     WHERE 1 = 1
       AND A.PLN_REV = V_PLN_REV
       AND A.SCM_FAMILY_CD = 'NAND'
       AND A.LINE_GRP_CD = 'WFT'
       /* CUM 대상에 해당하는 STACK 으로 Total-WFT 생성하고, 해당사항이 없으면 '*' 으로 생성하도록 변경 */
       AND A.SCM_FAMILY_CD || A.FAB_ID || A.TECH_CD || A.FAB_DEN_CD || A.CELL_LAYER_TYP_CD || A.CHG_PROD_MODE_CD || NVL(TRIM(A.FAB2_CD), '*') || '_' || NVL(TRIM(A.PKG_TYP_CD2), '*')
                                      IN (
                                            SELECT DISTINCT A.SCM_FAMILY_CD || A.FAB_ID || A.TECH_CD || A.FAB_DEN_CD || A.CELL_LAYER_TYP_CD || A.CHG_PROD_MODE_CD || NVL(TRIM(A.FAB2_CD), '*') || '_' ||NVL(B.PKG_TYP_CD2, '*')
									       									    FROM RPO_MFG_YIELD A
                                                 , (
                                                   		SELECT DISTINCT PLN_REV
                                                           , PLN_YM, PLN_WEEK_GBN_CD
                                                           , SCM_FAMILY_CD, FAB_ID, TECH_CD
                                                    			 , FAB_DEN_CD
                                                           , CELL_LAYER_TYP_CD
                                                           , FAB2_CD, TRIM(PKG_TYP_CD2) AS PKG_TYP_CD2
																						       		  FROM RPO_MFG_YIELD
																						           WHERE 1 = 1
																						             AND PLN_REV = V_PLN_REV
																						       			 AND SCM_FAMILY_CD = 'NAND'
                                                         AND LINE_GRP_CD   = 'WFT'
                                                   ) B
									                           WHERE 1 = 1
                                               AND A.PLN_REV 						  = B.PLN_REV(+)
                                               AND A.PLN_YM							  = B.PLN_YM(+)
                                               AND A.PLN_WEEK_GBN_CD 		  = B.PLN_WEEK_GBN_CD(+)
                                               AND A.SCM_FAMILY_CD 			  = B.SCM_FAMILY_CD(+)
                                               AND A.FAB_ID 						  = B.FAB_ID(+)
                                               AND A.TECH_CD 						  = B.TECH_CD(+)
                                               AND A.FAB_DEN_CD 				  = B.FAB_DEN_CD(+)
                                               AND A.CELL_LAYER_TYP_CD 	  = B.CELL_LAYER_TYP_CD(+)
                                               AND A.FAB2_CD 						  = B.FAB2_CD(+)
                                               AND A.PKG_TYP_CD2     		  = B.PKG_TYP_CD2(+)
									                             AND A.PLN_REV 						  = V_PLN_REV
									       									 		 AND A.SCM_FAMILY_CD 			  = 'NAND'
                                               AND A.CUM_YLD_APPLY_TGT_YN = 'Y'
                                               AND A.LINE_GRP_CD 				  = 'P_T'
									                        )

    UNION ALL

    -- PT_CUM 생성(Total)
    SELECT A.PLN_REV, A.SCM_FAMILY_CD, A.FAB_ID, A.TECH_CD, A.FAB_DEN_CD, A.CELL_LAYER_TYP_CD
         , 'Total' AS CHG_PROD_MODE_CD
         , A.SCM_PROD_VER_CD, A.NET_DIE_300_CNT, 'PT_CUM' AS LINE_GRP_CD, A.TSV_GBN_CD, A.PKG_TYP_CD2, A.PNT_PLN_SPCL_CD
         , A.ORG_SCM_FAMILY_CD, A.TGT_YM, A.PLN_YM, A.PLN_WEEK_GBN_CD, A.YLD, A.FAB2_CD
		     , 'N' AS CUM_YLD_APPLY_TGT_YN, A.SORT_SEQ
         , SYSDATE, 'MFG_YIELD_SP(TOTAL)', '' AS CHG_TM, '' AS CHG_USER_ID
      FROM RPO_MFG_YIELD A
     WHERE 1 = 1
       AND A.PLN_REV = V_PLN_REV
       AND A.SCM_FAMILY_CD = 'NAND'
       AND A.CUM_YLD_APPLY_TGT_YN = 'Y'
       AND A.LINE_GRP_CD = 'P_T'
    ;

    COMMIT;
    -- ==========================================================================================================================================================

   	DBMS_OUTPUT.PUT_LINE('**********[ cum YIELD INSERT  ] **********'||'-'|| TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS'));

    -- CUM1,2 YIELD INSERT
   	INSERT INTO RPO_MFG_YIELD(PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD, NET_DIE_300_CNT, LINE_GRP_CD, TSV_GBN_CD, PKG_TYP_CD2, PNT_PLN_SPCL_CD
    											  , ORG_SCM_FAMILY_CD, TGT_YM, PLN_YM, PLN_WEEK_GBN_CD, YLD, FAB2_CD, CUM_YLD_APPLY_TGT_YN, SORT_SEQ, CRT_TM, CRT_USER_ID, CHG_TM, CHG_USER_ID)
   	WITH FAB_CUM_TBL AS
    (
    		SELECT PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD, NET_DIE_300_CNT, LINE_GRP_CD, TSV_GBN_CD, PKG_TYP_CD2, PNT_PLN_SPCL_CD
         		 , ORG_SCM_FAMILY_CD, TGT_YM, PLN_YM, PLN_WEEK_GBN_CD, YLD, FAB2_CD, CUM_YLD_APPLY_TGT_YN, SORT_SEQ--, CRT_TM, CRT_USER_ID, CHG_TM, CHG_USER_ID --21.09.01 JHS 불필요
          FROM RPO_MFG_YIELD
         WHERE PLN_REV = V_PLN_REV
           AND LINE_GRP_CD = 'FAB'
           AND FAB2_CD NOT LIKE '%BASE%'
           AND (SCM_FAMILY_CD = 'DRAM' OR ( SCM_FAMILY_CD = 'NAND' AND CHG_PROD_MODE_CD = 'Total'))			--■■■ 로직변경(2023.10)
   	)
   	,WFT_CUM_TBL AS
    (
        SELECT PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD, NET_DIE_300_CNT, LINE_GRP_CD, TSV_GBN_CD, PKG_TYP_CD2, PNT_PLN_SPCL_CD
        			, ORG_SCM_FAMILY_CD, TGT_YM, PLN_YM, PLN_WEEK_GBN_CD, YLD, FAB2_CD, CUM_YLD_APPLY_TGT_YN, SORT_SEQ--, CRT_TM, CRT_USER_ID, CHG_TM, CHG_USER_ID --21.09.01 JHS 불필요
          FROM RPO_MFG_YIELD
         WHERE PLN_REV = V_PLN_REV
           AND LINE_GRP_CD = 'WFT'
           AND FAB2_CD NOT LIKE '%BASE%'
           AND (SCM_FAMILY_CD = 'DRAM' OR ( SCM_FAMILY_CD = 'NAND' AND CHG_PROD_MODE_CD = 'Total'))		--■■■ 로직변경(2023.10)
   	)
   	, P_T_CUM_TBL AS
    (
				--5가지 Type으로 구분
        --1. SCM_PKG_TYP_CD4 존재 (SCM_PKG_TYP_CD4만 유지)
        --2. PNT_UNUS_OPER_VAL 존재 (PNT_UNUS_OPER_VAL, PKG_TYP_CD2 유지)
        --3. PKG_TYP_CD2 존재 (PKG_TYP_CD2 유지)
        --4. MODE = 'LPDDR4' AND PKG_TYP_CD2 존재 (PNT_UNUS_OPER_VAL = 'POP')
        --5. 그 외
         -- TSV 분리작업으로 아래쿼리로 변경 - (20230614)
         /*
         SELECT A.PLN_REV, A.SCM_FAMILY_CD, A.FAB_ID, A.TECH_CD, A.FAB_DEN_CD, REPLACE(A.CELL_LAYER_TYP_CD, 'iTLC', 'TLC') AS CELL_LAYER_TYP_CD
            , CASE WHEN A.SCM_FAMILY_CD = 'NAND' THEN 'Raw NAND' ELSE A.CHG_PROD_MODE_CD END AS CHG_PROD_MODE_CD
            , A.SCM_PROD_VER_CD, A.NET_DIE_300_CNT, 'PT_CUM' AS LINE_GRP_CD, A.TSV_GBN_CD
            , CASE WHEN A.SCM_FAMILY_CD = 'NAND' THEN ' ' ELSE A.PKG_TYP_CD2 END AS PKG_TYP_CD2, A.PNT_PLN_SPCL_CD
            , A.ORG_SCM_FAMILY_CD, A.TGT_YM, A.PLN_YM, A.PLN_WEEK_GBN_CD, A.YLD, A.FAB2_CD, A.CUM_YLD_APPLY_TGT_YN, SORT_SEQ --, CRT_TM, CRT_USER_ID, CHG_TM, CHG_USER_ID\ --21.09.01 JHS 불필요
            , CASE WHEN B.FAB2_CD IS NOT NULL THEN 1
                   WHEN C.FAB2_CD IS NOT NULL THEN 2
                   WHEN D.FAB2_CD IS NOT NULL THEN 3
                   WHEN E.FAB2_CD IS NOT NULL THEN 4
              ELSE 5 END AS GBN_CD   --'21.09.01 제품 Type에 따른 구분 추가
          FROM RPO_MFG_YIELD A
                , (SELECT DISTINCT FAB2_CD, TSV_GBN_CD FROM WFT_CUM_TBL WHERE TRIM(TSV_GBN_CD) IS NOT NULL) B  --1. SCM_PKG_TYP_CD4 존재
                , (SELECT DISTINCT FAB2_CD, PNT_PLN_SPCL_CD, PKG_TYP_CD2 FROM WFT_CUM_TBL WHERE TRIM(PNT_PLN_SPCL_CD) IS NOT NULL AND TRIM(PKG_TYP_CD2) IS NOT NULL) C   --2. PNT_UNUS_OPER_VAL 존재
                , (SELECT DISTINCT FAB2_CD, PKG_TYP_CD2 FROM WFT_CUM_TBL WHERE TRIM(PNT_PLN_SPCL_CD) IS NULL AND TRIM(PKG_TYP_CD2) IS NOT NULL) D   --3. PKG_TYP_CD2 존재
                , (SELECT DISTINCT FAB2_CD||'DRAM' AS FAB2_CD FROM WFT_CUM_TBL WHERE TRIM(PNT_PLN_SPCL_CD) IS NOT NULL AND TRIM(PKG_TYP_CD2) IS NULL) E   --4. MODE = 'LPDDR' AND PKG_TYP_CD2 존재
         WHERE A.PLN_REV = V_PLN_REV
           AND A.LINE_GRP_CD = 'P_T'
           AND A.CUM_YLD_APPLY_TGT_YN = 'Y'
           AND A.FAB2_CD NOT LIKE '%BASE%'
           --AND CHG_PROD_MODE_CD NOT LIKE '%HBM%'
           --'21.09.01 제품 Type에 따른 구분 추가
           --1
           AND A.FAB2_CD = B.FAB2_CD(+)
           AND A.TSV_GBN_CD = B.TSV_GBN_CD(+)
           --2
           AND A.FAB2_CD = C.FAB2_CD(+)
           AND A.PNT_PLN_SPCL_CD = C.PNT_PLN_SPCL_CD(+)
           AND A.PKG_TYP_CD2 = C.PKG_TYP_CD2(+)
           --3
           AND A.FAB2_CD = D.FAB2_CD(+)
           AND A.PKG_TYP_CD2 = D.PKG_TYP_CD2(+)
           --4
           AND A.FAB2_CD||A.ORG_SCM_FAMILY_CD = E.FAB2_CD(+)
         */
         SELECT A.PLN_REV, A.SCM_FAMILY_CD, A.FAB_ID, A.TECH_CD, A.FAB_DEN_CD, A.CELL_LAYER_TYP_CD
					    , A.CHG_PROD_MODE_CD
					    , A.SCM_PROD_VER_CD, A.NET_DIE_300_CNT, A.LINE_GRP_CD, A.TSV_GBN_CD
					    , A.PKG_TYP_CD2, A.PNT_PLN_SPCL_CD
					    , A.ORG_SCM_FAMILY_CD, A.TGT_YM, A.PLN_YM, A.PLN_WEEK_GBN_CD, A.YLD, A.FAB2_CD, A.CUM_YLD_APPLY_TGT_YN, SORT_SEQ
					    , A.GBN_CD
           FROM (
					         SELECT A.PLN_REV, A.SCM_FAMILY_CD, A.FAB_ID, A.TECH_CD, A.FAB_DEN_CD, REPLACE(A.CELL_LAYER_TYP_CD, 'iTLC', 'TLC') AS CELL_LAYER_TYP_CD

						            --■■■ 로직변경(2023.10)
                        --, CASE WHEN A.SCM_FAMILY_CD = 'NAND' THEN 'Raw NAND' ELSE A.CHG_PROD_MODE_CD END AS CHG_PROD_MODE_CD
                        , CASE WHEN A.SCM_FAMILY_CD = 'NAND' THEN 'Total' ELSE A.CHG_PROD_MODE_CD END AS CHG_PROD_MODE_CD

						            , A.SCM_PROD_VER_CD, A.NET_DIE_300_CNT, 'PT_CUM' AS LINE_GRP_CD, A.TSV_GBN_CD
						            , CASE WHEN A.SCM_FAMILY_CD = 'NAND' THEN ' ' ELSE A.PKG_TYP_CD2 END AS PKG_TYP_CD2, A.PNT_PLN_SPCL_CD
						            , A.ORG_SCM_FAMILY_CD, A.TGT_YM, A.PLN_YM, A.PLN_WEEK_GBN_CD, A.YLD, A.FAB2_CD, A.CUM_YLD_APPLY_TGT_YN, SORT_SEQ --, CRT_TM, CRT_USER_ID, CHG_TM, CHG_USER_ID\ --21.09.01 JHS 불필요
						            , CASE WHEN B.FAB2_CD IS NOT NULL THEN 1
						                   WHEN C.FAB2_CD IS NOT NULL THEN 2
						                   WHEN D.FAB2_CD IS NOT NULL THEN 3
						                   WHEN E.FAB2_CD IS NOT NULL THEN 4
						              ELSE 5 END AS GBN_CD   --'21.09.01 제품 Type에 따른 구분 추가
		                    , RANK( ) OVER (PARTITION BY A.PLN_REV, A.FAB2_CD, DECODE(A.TSV_GBN_CD, 'TSV', 'TSV', '*') ORDER BY DECODE(A.CUM_YLD_APPLY_TGT_YN, 'Y', 1, 2), DECODE(A.PKG_TYP_CD2, 'SDP', 1, 'DDP', 2, 'QDP',3, 4) )  AS RNK
					           FROM RPO_MFG_YIELD A
					              /* ■ 아래 조건으로 수정(2023.10.12)■ */
                        /*
					              , (SELECT DISTINCT FAB2_CD, TSV_GBN_CD FROM WFT_CUM_TBL WHERE TRIM(TSV_GBN_CD) IS NOT NULL) B  --1. SCM_PKG_TYP_CD4 존재
					              , (SELECT DISTINCT FAB2_CD, PNT_PLN_SPCL_CD, PKG_TYP_CD2 FROM WFT_CUM_TBL WHERE TRIM(PNT_PLN_SPCL_CD) IS NOT NULL AND TRIM(PKG_TYP_CD2) IS NOT NULL) C   --2. PNT_UNUS_OPER_VAL 존재
					              , (SELECT DISTINCT FAB2_CD, PKG_TYP_CD2 FROM WFT_CUM_TBL WHERE TRIM(PNT_PLN_SPCL_CD) IS NULL AND TRIM(PKG_TYP_CD2) IS NOT NULL) D   --3. PKG_TYP_CD2 존재
					              , (SELECT DISTINCT FAB2_CD||'DRAM' AS FAB2_CD FROM WFT_CUM_TBL WHERE TRIM(PNT_PLN_SPCL_CD) IS NOT NULL AND TRIM(PKG_TYP_CD2) IS NULL) E   --4. MODE = 'LPDDR' AND PKG_TYP_CD2 존재
                        */
                        , (SELECT DISTINCT FAB2_CD, TSV_GBN_CD FROM WFT_CUM_TBL WHERE  NVL(TSV_GBN_CD, '*') <> '*') B  --1. SCM_PKG_TYP_CD4 존재
					              , (SELECT DISTINCT FAB2_CD, PNT_PLN_SPCL_CD, PKG_TYP_CD2 FROM WFT_CUM_TBL WHERE NVL(PNT_PLN_SPCL_CD, '*') <> '*' AND NVL(PKG_TYP_CD2, '*') <> '*') C   --2. PNT_UNUS_OPER_VAL 존재
                        , (SELECT DISTINCT FAB2_CD, PKG_TYP_CD2 FROM WFT_CUM_TBL WHERE NVL(PNT_PLN_SPCL_CD, '*') = '*' AND NVL(PKG_TYP_CD2, '*') <> '*') D
					              , (SELECT DISTINCT FAB2_CD||'DRAM' AS FAB2_CD FROM WFT_CUM_TBL WHERE NVL(PNT_PLN_SPCL_CD, '*') <> '*' AND NVL(PKG_TYP_CD2, '*') = '*') E   --4. MODE = 'LPDDR' AND PKG_TYP_CD2 존재
					         WHERE A.PLN_REV = V_PLN_REV
					           AND A.LINE_GRP_CD = 'P_T'
					           --AND A.CUM_YLD_APPLY_TGT_YN = 'Y'
	                   AND (A.CUM_YLD_APPLY_TGT_YN = 'Y' OR A.TSV_GBN_CD = 'TSV')    --■ 추가(2023.06.14)
					           AND A.FAB2_CD NOT LIKE '%BASE%'
					           --AND CHG_PROD_MODE_CD NOT LIKE '%HBM%'
					           /*'21.09.01 제품 Type에 따른 구분 추가*/
					           --1
					           AND A.FAB2_CD = B.FAB2_CD(+)
					           AND A.TSV_GBN_CD = B.TSV_GBN_CD(+)
					           --2
					           AND A.FAB2_CD = C.FAB2_CD(+)
					           AND A.PNT_PLN_SPCL_CD = C.PNT_PLN_SPCL_CD(+)
					           AND A.PKG_TYP_CD2 = C.PKG_TYP_CD2(+)
					           --3
					           AND A.FAB2_CD = D.FAB2_CD(+)
					           AND A.PKG_TYP_CD2 = D.PKG_TYP_CD2(+)
					           --4
					           AND A.FAB2_CD||A.ORG_SCM_FAMILY_CD = E.FAB2_CD(+)
                ) A
          WHERE 1 = 1
            AND A.RNK = 1
   	)
   	, CUM1_TBL AS
    (
         SELECT A.PLN_REV, A.SCM_FAMILY_CD, A.FAB_ID, A.TECH_CD, A.FAB_DEN_CD, A.CELL_LAYER_TYP_CD

         			--■■■ 로직변경(2023.10)
              --, A.CHG_PROD_MODE_CD
				      , CASE WHEN A.SCM_FAMILY_CD = 'NAND' THEN 'Total' ELSE A.CHG_PROD_MODE_CD END AS CHG_PROD_MODE_CD

              , A.SCM_PROD_VER_CD, A.NET_DIE_300_CNT, 'CUM1' AS LINE_GRP_CD, A.TSV_GBN_CD, A.PKG_TYP_CD2, A.PNT_PLN_SPCL_CD
              , A.ORG_SCM_FAMILY_CD, A.TGT_YM, A.PLN_YM, A.PLN_WEEK_GBN_CD
              , A.CUM1_YLD AS YLD
              , A.FAB2_CD, A.CUM_YLD_APPLY_TGT_YN
              , A.SORT_SEQ--, A.CRT_TM, A.CRT_USER_ID, A.CHG_TM, A.CHG_USER_ID  --21.09.01 JHS 불필요 주석 처리
           FROM (
				            /*'21.09.01 제품 Type에 따른 LOGIC 수정*/
				            --1. SCM_PKG_TYP_CD4 존재
				            SELECT A.*, A.YLD * B.YLD AS CUM1_YLD
				            FROM P_T_CUM_TBL A
				                , WFT_CUM_TBL B
				            WHERE A.GBN_CD = 1
				                AND A.FAB2_CD = B.FAB2_CD(+)
				                AND A.TSV_GBN_CD = B.TSV_GBN_CD(+)
				                AND A.TGT_YM = B.TGT_YM(+)

				            UNION ALL

				        --2. PNT_UNUS_OPER_VAL 존재
				            SELECT A.*, A.YLD * B.YLD AS CUM1_YLD
				            FROM P_T_CUM_TBL A
				                , WFT_CUM_TBL B
				            WHERE A.GBN_CD = 2
				                AND A.FAB2_CD = B.FAB2_CD(+)
				                AND A.PNT_PLN_SPCL_CD = B.PNT_PLN_SPCL_CD(+)
				                AND A.PKG_TYP_CD2 = B.PKG_TYP_CD2(+)
				                AND A.TGT_YM = B.TGT_YM(+)

				            UNION ALL

				        --3. PKG_TYP_CD2 존재
				            SELECT A.*, A.YLD * B.YLD AS CUM1_YLD
				            FROM P_T_CUM_TBL A
				                , WFT_CUM_TBL B
				            WHERE A.GBN_CD = 3
				                AND A.FAB2_CD = B.FAB2_CD(+)
				                AND A.PKG_TYP_CD2 = B.PKG_TYP_CD2(+)
				                AND A.TGT_YM = B.TGT_YM(+)

				            UNION ALL

				        --4. MODE = 'LPDDR' AND PKG_TYP_CD2 존재(2023.06.30 POP제품 POP WT수율이 아닌, Normal WT수율 반영되도록 IS NOT NULL -> IS NULL로 수정)
				            SELECT A.*, A.YLD * B.YLD AS CUM1_YLD
				            FROM P_T_CUM_TBL A
				                , (SELECT * FROM WFT_CUM_TBL WHERE TRIM(PNT_PLN_SPCL_CD) IS NULL AND TRIM(PKG_TYP_CD2) IS NULL) B
				            WHERE A.GBN_CD = 4
				                AND A.FAB2_CD = B.FAB2_CD(+)
				                AND A.TGT_YM = B.TGT_YM(+)

				            UNION ALL

				        --5. 기타
				            SELECT A.*, A.YLD * B.YLD AS CUM1_YLD
				            FROM P_T_CUM_TBL A
				                , (SELECT * FROM WFT_CUM_TBL WHERE TRIM(PNT_PLN_SPCL_CD) IS NULL AND TRIM(PKG_TYP_CD2) IS NULL AND TRIM(TSV_GBN_CD) IS NULL) B
				            WHERE A.GBN_CD = 5
				                AND A.FAB2_CD = B.FAB2_CD(+)
				                AND A.TGT_YM = B.TGT_YM(+)
             		) A
        	WHERE A.CUM1_YLD > 0
   	)
   	, CUM2_TBL AS
    (
    		SELECT A.PLN_REV, A.SCM_FAMILY_CD, A.FAB_ID, A.TECH_CD, A.FAB_DEN_CD, A.CELL_LAYER_TYP_CD

         		 --■■■ 로직변경(2023.10)
             --, A.CHG_PROD_MODE_CD
				     , CASE WHEN A.SCM_FAMILY_CD = 'NAND' THEN 'Total' ELSE A.CHG_PROD_MODE_CD END AS CHG_PROD_MODE_CD

	           , A.SCM_PROD_VER_CD, A.NET_DIE_300_CNT, 'CUM2' AS LINE_GRP_CD, A.TSV_GBN_CD, A.PKG_TYP_CD2, A.PNT_PLN_SPCL_CD
	           , A.ORG_SCM_FAMILY_CD, A.TGT_YM, A.PLN_YM, A.PLN_WEEK_GBN_CD
	           , (A.YLD * NVL(B.YLD, C.YLD)) AS YLD
	           , A.FAB2_CD, A.CUM_YLD_APPLY_TGT_YN
	           , A.SORT_SEQ--, A.CRT_TM, A.CRT_USER_ID, A.CHG_TM, A.CHG_USER_ID  --21.09.01 JHS 불필요 주석처리
	        FROM CUM1_TBL A
	           , (SELECT * FROM FAB_CUM_TBL WHERE TRIM(TSV_GBN_CD) IS NOT NULL) B  --TSV_GBN_CD MAPPING
	           , (SELECT * FROM FAB_CUM_TBL WHERE TRIM(TSV_GBN_CD) IS NULL) C
	       WHERE A.FAB2_CD = B.FAB2_CD(+)
	         AND A.TSV_GBN_CD = B.TSV_GBN_CD(+)
	         AND A.TGT_YM = B.TGT_YM(+)
	         AND A.FAB2_CD = C.FAB2_CD(+)
	         AND A.TGT_YM = C.TGT_YM(+)
	         AND (A.YLD * NVL(NVL(B.YLD, C.YLD), 0)) > 0
   	)
    SELECT PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD, NET_DIE_300_CNT, LINE_GRP_CD
         -- , TSV_GBN_CD, PKG_TYP_CD2, PNT_PLN_SPCL_CD, ORG_SCM_FAMILY_CD
         -- , ' ' AS TSV_GBN_CD
         , TSV_GBN_CD AS TSV_GBN_CD  --■ 변경(2023.06.14)
         , ' ' AS PKG_TYP_CD2, ' ' AS PNT_PLN_SPCL_CD, ' ' AS ORG_SCM_FAMILY_CD --'21.04.06 실적 연계 관련 수정
         , TGT_YM, PLN_YM, PLN_WEEK_GBN_CD, MAX(YLD), FAB2_CD, '' AS CUM_YLD_APPLY_TGT_YN, SORT_SEQ, SYSDATE AS CRT_TM, 'MFG_YIELD_SP' AS CRT_USER_ID, '' AS CHG_TM, '' AS CHG_USER_ID
      FROM (
            		SELECT *
                  FROM P_T_CUM_TBL
                 WHERE FAB2_CD IN (SELECT DISTINCT FAB2_CD FROM CUM1_TBL)
                   AND SCM_FAMILY_CD = 'DRAM'

                UNION ALL

                SELECT A.*, 0 AS GBN_CD FROM CUM1_TBL A

                UNION ALL

                SELECT A.*, 0 AS GBN_CD FROM CUM2_TBL A
           )
        --2022.11.08 동일 주키에 대해, 두개의 YLD 존재로 인해 MAX로 임시 처리
     GROUP BY PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, CHG_PROD_MODE_CD
            , SCM_PROD_VER_CD, NET_DIE_300_CNT, LINE_GRP_CD
            , TSV_GBN_CD    			--■ 추가(2023.06.14)
            , TGT_YM, PLN_YM, PLN_WEEK_GBN_CD, FAB2_CD, SORT_SEQ
   	;

   	-- FAMILY, FAB 별 수율 INSERT
   	IF V_CUM_GUBUN <> 'Y'  THEN
     		-- FAMILY, FAB별 수율
       	DBMS_OUTPUT.PUT_LINE('**********[ family,fab group cum YIELD INSERT  ] **********'||'-'|| TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS'));
        INSERT INTO RPO_MFG_YIELD(PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD, NET_DIE_300_CNT, LINE_GRP_CD, TSV_GBN_CD, PKG_TYP_CD2, PNT_PLN_SPCL_CD,
                                   ORG_SCM_FAMILY_CD, TGT_YM, PLN_YM, PLN_WEEK_GBN_CD, YLD, FAB2_CD, CUM_YLD_APPLY_TGT_YN, SORT_SEQ, CRT_TM, CRT_USER_ID, CHG_TM, CHG_USER_ID)
        WITH WFT_DRAM_PORTION_GRP AS
        (
             SELECT  PLN_REV, PRTN_TYP_CD, LINE_CD, FAB_ID, RP_CD, PROD_GRP_CD, PRTN_DATA_GBN_CD, TGT_YM, (1-NVL(YLD,0)) AS YLD , FAB2_CD
               FROM  RPI_PORTION
              WHERE  PLN_REV = V_PLN_REV
                AND   PRTN_TYP_CD = 'GRADE'
                AND   LINE_CD = 'WFT'
                AND   PRTN_DATA_GBN_CD = 'PLN'
        )
        , WFT_FLASH_PORTION_GRP AS
        (
             SELECT  PLN_REV, PRTN_TYP_CD, LINE_CD, FAB_ID, RP_CD, PROD_GRP_CD, PRTN_DATA_GBN_CD, TGT_YM, (1-NVL(YLD,0)) AS YLD , FAB2_CD
               FROM  RPI_PORTION
              WHERE  PLN_REV = V_PLN_REV
                AND   PRTN_TYP_CD = 'GRADE'
                AND   LINE_CD = 'PKG'
                AND   PRTN_DATA_GBN_CD = 'PLN'
        )
        , WFT_MFG_RP_CD_GRP AS
        (
             SELECT ORG_RP_CD AS RP_CD, LINE_MIX_CD,  TGT_YM, PLN_DATA_VAL FROM  RPO_LINE_MFG_PLN_MG_VW
              WHERE  1=1
                AND   PLN_REV = V_PLN_REV
                AND   LINE_MIX_CD = 'WFT'
                AND   PLN_TYP_CD = 'OUT'
        )
        , WFT_YLD_TBL_FAMILY_GRP AS
        (
        		SELECT D.SCM_FAMILY_CD, C.LINE_GRP_CD, C.TGT_YM
                 , CASE WHEN Nvl(Sum(B.PLN_DATA_VAL),0) = 0 THEN 0 ELSE Round(SUM(B.PLN_DATA_VAL * C.YLD * DECODE(D.SCM_FAMILY_CD,'DRAM',NVL(E.YLD,1),'NAND',NVL(F.YLD,1),1)) / Sum(B.PLN_DATA_VAL),5) END AS YLD
              FROM (SELECT DISTINCT WFT_CD, FA2_CD FROM RPI_FGS_COMP_BOM) A
                 , WFT_MFG_RP_CD_GRP B
                 , RPI_YIELD C
                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN='Y') D
                 , WFT_DRAM_PORTION_GRP E
                 , WFT_FLASH_PORTION_GRP F
             WHERE 1 = 1
               AND C.PLN_REV = V_PLN_REV
               AND C.LINE_GRP_CD = 'WFT'
               AND C.YLD_GBN_CD = 'PLN'
               AND A.WFT_CD = C.RP_CD  -- BOM에 있는 RP_CD만 대상으로함.
               AND C.RP_CD = B.RP_CD   -- MFG 생산계획에 있는 가중평균.
               AND C.LINE_GRP_CD = B.LINE_MIX_CD
               AND C.TGT_YM = B.TGT_YM
               AND C.RP_CD = D.RP_CD(+)
               AND C.RP_CD = E.RP_CD(+)
               AND C.TGT_YM = E.TGT_YM(+)
               AND C.RP_CD = F.RP_CD(+)
               AND C.TGT_YM = F.TGT_YM(+)
             GROUP BY D.SCM_FAMILY_CD, C.LINE_GRP_CD, C.TGT_YM
            HAVING Nvl(Sum(B.PLN_DATA_VAL),0) > 0
        )
        , WFT_YLD_TBL_FAB_GRP AS
        (
        		SELECT D.SCM_FAMILY_CD, C.FAB_ID, C.LINE_GRP_CD, C.TGT_YM
                 , CASE WHEN Nvl(Sum(B.PLN_DATA_VAL),0) = 0 THEN 0 ELSE Round(SUM(B.PLN_DATA_VAL * C.YLD * DECODE(D.SCM_FAMILY_CD,'DRAM',NVL(E.YLD,1),'NAND',NVL(F.YLD,1),1)) / Sum(B.PLN_DATA_VAL),5) END AS YLD
              FROM (SELECT DISTINCT WFT_CD, FA2_CD FROM RPI_FGS_COMP_BOM) A
                 , WFT_MFG_RP_CD_GRP B
                 , RPI_YIELD C
                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN='Y') D
                 , WFT_DRAM_PORTION_GRP E
                 , WFT_FLASH_PORTION_GRP F
             WHERE 1 = 1
               AND C.PLN_REV = V_PLN_REV
               AND C.LINE_GRP_CD = 'WFT'
               AND C.YLD_GBN_CD = 'PLN'
               AND A.WFT_CD = C.RP_CD  -- BOM에 있는 RP_CD만 대상으로함.
               AND C.RP_CD = B.RP_CD   -- MFG 생산계획에 있는 가중평균.
               AND C.LINE_GRP_CD = B.LINE_MIX_CD
               AND C.TGT_YM = B.TGT_YM
               AND C.RP_CD = D.RP_CD(+)
               AND C.RP_CD = E.RP_CD(+)
               AND C.TGT_YM = E.TGT_YM(+)
               AND C.RP_CD = F.RP_CD(+)
               AND C.TGT_YM = F.TGT_YM(+)
             GROUP BY D.SCM_FAMILY_CD, C.FAB_ID,  C.LINE_GRP_CD, C.TGT_YM
            HAVING Nvl(Sum(B.PLN_DATA_VAL),0) > 0
        )   -- END IF  WFT GRP
        , WLP_BOM_TBL_GRP AS
        (
            SELECT TO_RP_CD, Max(FR_RP_CD) AS FR_RP_CD
              FROM RPI_RPBOM_I
             WHERE LINE_CD = 'PKG'
               AND FR_RP_CD LIKE '%WLP'
               AND USE_YN = 'Y'
             GROUP BY TO_RP_CD
        )
        ,WLP_TBL_GRP AS
        (
            SELECT A.PLN_REV, A.LINE_GRP_CD, A.FAB_ID, A.RP_CD,  A.TGT_YM, A.YLD , A.YLD_UNIT_CD
                 , B.TO_RP_CD
              FROM RPI_YIELD A,  WLP_BOM_TBL_GRP B
             WHERE 1 = 1
               AND A.PLN_REV = V_PLN_REV
               AND A.LINE_GRP_CD = 'WLP'
               AND A.YLD_GBN_CD = 'PLN'
               AND A.RP_CD = B.FR_RP_CD(+)
        )
        ,PKG_TBL_GRP AS
        (
            SELECT A.PLN_REV, A.LINE_GRP_CD, A.FAB_ID, A.RP_CD
                 --,B.FR_RP_CD AS WLP_CD
                 , A.TGT_YM, A.YLD  , A.YLD_UNIT_CD
              FROM RPI_YIELD A
               --, WLP_BOM_TBL_GRP B
             WHERE 1 = 1
               AND A.PLN_REV = V_PLN_REV
               AND A.LINE_GRP_CD = 'PKG'
               AND A.YLD_GBN_CD = 'PLN'
               -- AND A.RP_CD = B.TO_RP_CD(+)
        )
        ,PKT_TBL_GRP AS
        (
            SELECT A.PLN_REV, A.LINE_GRP_CD, A.FAB_ID, A.RP_CD
               --, B.FR_RP_CD AS PKG_CD
                 , A.TGT_YM, A.YLD, A.YLD_UNIT_CD
              FROM RPI_YIELD A   --, PKG_BOM_TBL_GRP B
             WHERE 1=1
               AND A.PLN_REV = V_PLN_REV
               AND A.LINE_GRP_CD = 'PKT'
               AND A.YLD_GBN_CD = 'PLN'
               --AND A.RP_CD = B.TO_RP_CD
        )
        , PKG_YLD_TBL_FAMILY_GRP AS
        (

            SELECT E.SCM_FAMILY_CD, B.LINE_GRP_CD, A.TGT_YM
                 , CASE WHEN Nvl(Sum(A.PLN_DATA_VAL),0) = 0 THEN 0 ELSE Round(SUM(A.PLN_DATA_VAL * Nvl(B.YLD,0) * Nvl(C.YLD,1)) / Sum(A.PLN_DATA_VAL),5) END AS YLD
              FROM RPO_LINE_MFG_PLN_MG_VW A
                 , PKG_TBL_GRP B
                 , WLP_TBL_GRP C
                 , RPI_FGS_COMP_BOM D
                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN='Y') E
             WHERE 1 = 1
               AND A.PLN_REV = V_PLN_REV
               AND A.LINE_MIX_CD = 'PKG'
               AND A.PLN_TYP_CD = 'OUT'
               AND A.LINE_MIX_CD = B.LINE_GRP_CD
               AND A.ORG_RP_CD = B.RP_CD
               AND A.TGT_YM = B.TGT_YM
               AND B.FAB_ID = C.FAB_ID(+)
               --AND   B.WLP_CD = C.RP_CD(+)
               AND B.RP_CD = C.TO_RP_CD(+)
               AND B.TGT_YM = C.TGT_YM(+)
               AND A.RP_CD = CASE WHEN A.ORG_SCM_FAMILY_CD = 'Hybrid' THEN D.FGS_CD(+) ELSE D.PKG_CD(+) END
               AND A.RP_CD = E.RP_CD(+)
             GROUP BY E.SCM_FAMILY_CD, B.LINE_GRP_CD, A.TGT_YM
            HAVING Nvl(Sum(A.PLN_DATA_VAL),0) > 0
        )
        , PKG_YLD_TBL_FAB_GRP AS
        (
            SELECT E.SCM_FAMILY_CD, B.LINE_GRP_CD, A.FAB_ID, A.TGT_YM
                 , CASE WHEN Nvl(Sum(A.PLN_DATA_VAL),0) = 0 THEN 0 ELSE Round(SUM(A.PLN_DATA_VAL * Nvl(B.YLD,0) * Nvl(C.YLD,1)) / Sum(A.PLN_DATA_VAL),5) END AS YLD
              FROM RPO_LINE_MFG_PLN_MG_VW A
                 , PKG_TBL_GRP B
                 , WLP_TBL_GRP C
                 , RPI_FGS_COMP_BOM D
                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN='Y') E
             WHERE 1 = 1
               AND A.PLN_REV = V_PLN_REV
               AND A.LINE_MIX_CD = 'PKG'
               AND A.PLN_TYP_CD = 'OUT'
               AND A.LINE_MIX_CD = B.LINE_GRP_CD
               AND A.ORG_RP_CD = B.RP_CD
               AND A.TGT_YM = B.TGT_YM
               AND B.FAB_ID = C.FAB_ID(+)
              -- AND   B.WLP_CD = C.RP_CD(+)
               AND B.RP_CD = C.TO_RP_CD(+)
               AND B.TGT_YM = C.TGT_YM(+)
               AND A.RP_CD = CASE WHEN A.ORG_SCM_FAMILY_CD = 'Hybrid' THEN D.FGS_CD(+) ELSE D.PKG_CD(+) END
               AND A.RP_CD = E.RP_CD(+)
             GROUP BY E.SCM_FAMILY_CD, B.LINE_GRP_CD, A.FAB_ID, A.TGT_YM
            HAVING Nvl(Sum(A.PLN_DATA_VAL),0) > 0
        )  -- END OF PKG GRP
        , PKC_DRAM_PORTION_GRP AS
        (
            SELECT PLN_REV, PRTN_TYP_CD, LINE_CD, FAB_ID, RP_CD, PROD_GRP_CD, PRTN_DATA_GBN_CD, TGT_YM, (1-NVL(YLD,0)) AS YLD , FAB2_CD
              FROM RPI_PORTION
             WHERE PLN_REV = V_PLN_REV
               AND PRTN_TYP_CD = 'GRADE'
               AND LINE_CD = 'PKC'
               AND PRTN_DATA_GBN_CD = 'PLN'
        )
        , PKT_YLD_TBL_FAMILY_GRP AS
        (
        		SELECT E.SCM_FAMILY_CD, B.LINE_GRP_CD, A.TGT_YM
                 , CASE WHEN Nvl(Sum(A.PLN_DATA_VAL),0) = 0 THEN 0 ELSE (Round(SUM(A.PLN_DATA_VAL * Nvl(B.YLD,0)) / Sum(A.PLN_DATA_VAL),5))* MAX(DECODE(E.SCM_FAMILY_CD,'DRAM',NVL(F.YLD,1),1)) END AS YLD, MAX(D.FA2_CD) AS FA2_CD
              FROM RPO_LINE_MFG_PLN_MG_VW A
                 , PKT_TBL_GRP B
                 , RPI_FGS_COMP_BOM D
                 , (SELECT * FROM STI_RPCODE_M WHERE NEW_YN='Y') E
                 , PKC_DRAM_PORTION_GRP F
             WHERE 1 = 1
               AND A.PLN_REV = V_PLN_REV
               AND A.LINE_MIX_CD = 'PKC'
               AND A.PLN_TYP_CD = 'OUT'
               AND A.LINE_MIX_CD = CASE WHEN B.LINE_GRP_CD = 'PKT' THEN 'PKC'
                                        ELSE B.LINE_GRP_CD
                                   END
               AND A.ORG_RP_CD = B.RP_CD
               AND A.TGT_YM = B.TGT_YM
               AND A.RP_CD = CASE WHEN A.ORG_SCM_FAMILY_CD = 'Hybrid' THEN D.FGS_CD(+) ELSE D.PKC_CD(+) END
               AND A.RP_CD = E.RP_CD(+)
               AND B.RP_CD = F.RP_CD(+)
               AND B.TGT_YM = F.TGT_YM(+)
             GROUP BY E.SCM_FAMILY_CD, B.LINE_GRP_CD, A.TGT_YM
            HAVING Nvl(Sum(A.PLN_DATA_VAL),0) > 0
        )
        , PKT_YLD_TBL_FAB_GRP AS
        (
               SELECT E.SCM_FAMILY_CD, B.LINE_GRP_CD, A.FAB_ID, A.TGT_YM
                     ,CASE WHEN Nvl(Sum(A.PLN_DATA_VAL),0) = 0 THEN 0 ELSE (Round(SUM(A.PLN_DATA_VAL * Nvl(B.YLD,0)) / Sum(A.PLN_DATA_VAL),5))* MAX(DECODE(E.SCM_FAMILY_CD,'DRAM',NVL(F.YLD,1),1)) END AS YLD, MAX(D.FA2_CD) AS FA2_CD
               FROM   RPO_LINE_MFG_PLN_MG_VW A
                     ,PKT_TBL_GRP B
                     ,RPI_FGS_COMP_BOM D
                     ,(SELECT * FROM STI_RPCODE_M WHERE NEW_YN='Y') E
                     ,PKC_DRAM_PORTION_GRP F
               WHERE  1=1
               AND   A.PLN_REV = V_PLN_REV
               AND   A.LINE_MIX_CD = 'PKC'
               AND   A.PLN_TYP_CD = 'OUT'
               AND   A.LINE_MIX_CD = CASE WHEN B.LINE_GRP_CD = 'PKT' THEN 'PKC'
                                            ELSE B.LINE_GRP_CD
                                      END
               AND   A.ORG_RP_CD = B.RP_CD
               AND   A.TGT_YM = B.TGT_YM
               AND   A.RP_CD = CASE WHEN A.ORG_SCM_FAMILY_CD = 'Hybrid' THEN D.FGS_CD(+) ELSE D.PKC_CD(+) END
               AND   A.RP_CD = E.RP_CD(+)
               AND   B.RP_CD = F.RP_CD(+)
               AND   B.TGT_YM = F.TGT_YM(+)
               GROUP BY E.SCM_FAMILY_CD, B.LINE_GRP_CD, A.FAB_ID, A.TGT_YM
                 HAVING Nvl(Sum(A.PLN_DATA_VAL),0) > 0
        )
	      SELECT PLN_REV, SCM_FAMILY_CD, FAB_ID, TECH_CD, FAB_DEN_CD, CELL_LAYER_TYP_CD, CHG_PROD_MODE_CD, SCM_PROD_VER_CD, NET_DIE_300_CNT, LINE_GRP_CD, TSV_GBN_CD, PKG_TYP_CD2, PNT_PLN_SPCL_CD
             , ORG_SCM_FAMILY_CD, TGT_YM, PLN_YM, PLN_WEEK_GBN_CD, YLD, FAB2_CD, CUM_YLD_APPLY_TGT_YN, SORT_SEQ, SYSDATE AS CRT_TM, 'MFG_YIELD_SP' AS CRT_USER_ID, '' AS CHG_TM, '' AS CHG_USER_ID
          FROM
              (

                  -- FAMILY, FAB별 CUM1
                  SELECT V_PLN_REV AS PLN_REV, A.SCM_FAMILY_CD, A.FAB_ID, ' ' AS TECH_CD, ' ' AS FAB_DEN_CD, ' ' AS CELL_LAYER_TYP_CD, ' ' AS CHG_PROD_MODE_CD, ' ' AS SCM_PROD_VER_CD, 0 AS NET_DIE_300_CNT
                       , 'CUM1' AS LINE_GRP_CD, ' ' AS TSV_GBN_CD, ' ' AS PKG_TYP_CD2, ' ' AS PNT_PLN_SPCL_CD,' ' AS ORG_SCM_FAMILY_CD, A.TGT_YM, V_PLN_YM AS PLN_YM, V_PLN_WEEK_GBN_CD AS PLN_WEEK_GBN_CD
                       , (NVL(A.YLD,1) * NVL(B.YLD,1) * NVL(C.YLD,1)) AS YLD, 'FAB_AVG' AS FAB2_CD, '' AS CUM_YLD_APPLY_TGT_YN, 0 AS SORT_SEQ
                    FROM PKT_YLD_TBL_FAB_GRP A
                       , PKG_YLD_TBL_FAB_GRP B
                       , WFT_YLD_TBL_FAB_GRP C
                   WHERE 1 = 1
                     AND A.SCM_FAMILY_CD = B.SCM_FAMILY_CD
                     AND A.FAB_ID = B.FAB_ID
                     AND A.TGT_YM = B.TGT_YM
                     AND A.SCM_FAMILY_CD = C.SCM_FAMILY_CD
                     AND A.FAB_ID = C.FAB_ID
                     AND A.TGT_YM = C.TGT_YM

                  UNION ALL  -- FAMILLY별  CUM1

                  SELECT V_PLN_REV AS PLN_REV, A.SCM_FAMILY_CD, ' ' AS FAB_ID, ' ' AS TECH_CD, ' ' AS FAB_DEN_CD, ' ' AS CELL_LAYER_TYP_CD, ' ' AS CHG_PROD_MODE_CD, ' ' AS SCM_PROD_VER_CD, 0 AS NET_DIE_300_CNT
                       , 'CUM1' AS LINE_GRP_CD, ' ' AS TSV_GBN_CD, ' ' AS PKG_TYP_CD2, ' ' AS PNT_PLN_SPCL_CD,' ' AS ORG_SCM_FAMILY_CD, A.TGT_YM, V_PLN_YM AS PLN_YM, V_PLN_WEEK_GBN_CD AS PLN_WEEK_GBN_CD
                       , (NVL(A.YLD,1) * NVL(B.YLD,1) * NVL(C.YLD,1)) AS YLD, 'FMY_AVG' AS FAB2_CD, '' AS CUM_YLD_APPLY_TGT_YN, 0 AS SORT_SEQ
                    FROM PKT_YLD_TBL_FAMILY_GRP A
                       , PKG_YLD_TBL_FAMILY_GRP B
                       , WFT_YLD_TBL_FAMILY_GRP C
                   WHERE 1=1
                     AND A.SCM_FAMILY_CD = B.SCM_FAMILY_CD
                     AND A.TGT_YM = B.TGT_YM
                     AND A.SCM_FAMILY_CD = C.SCM_FAMILY_CD
                     AND A.TGT_YM = C.TGT_YM
              )
        ;
   	END IF;

   	COMMIT;

   	DBMS_OUTPUT.PUT_LINE('**********[ END OF ALL INSERT  ] **********'||'-'|| TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS'));

   	-- PLN REV 상태값 UPDATE
   	V_MCATG_PRGS_STAT_CD := 'C';  -- 중분류 R: RUNNING, C: COMPLETE      -- 20210623 중분류 상태도 같이 종료로 업데이트
   	V_SCATG_PRGS_STAT_CD := 'C';  -- 소분류 R: RUNNING, C: COMPLETE
   	V_WORK_SCATG_CD      := '10'; -- RPO_MFG_YIELD_SP
--    01 : RPO_SALE_PSI_RP           05 : RPO_EQP_OPRATIO_TOT_CAPA_SP
--    02 : RPO_LINE_MFG_PSI_SP       06 : RPO_BOH_SP
--    03 : RPO_SOM_DSATIS_CAUSE_SP   07 : RPO_WF_TEST_OUT_SP
--    04 : RPO_SITE_LINE_MFG_PLN_SP  08 : RPO_FGS_IN_PLAN_ADJUST_SP
--    09 : RPO_WF_TEST_OUT_PEG_SP    10 : RPO_MFG_YIELD_SP
   --DBMS_OUTPUT.PUT_LINE('#8 RPI_PLN_REV_STAT_UPDATE_SP - ' ||'-'|| TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS'));

    IF V_CUM_GUBUN <> 'Y'  THEN
        RPLS_ADM.RPI_PLN_REV_STAT_UPDATE_SP ( VI_PLN_REV, V_MCATG_PRGS_STAT_CD, V_SCATG_PRGS_STAT_CD, V_WORK_LCATG_CD, V_WORK_MCATG_CD, V_WORK_SCATG_CD, V_RETURN_VALUE );
   	END IF;


    /* ############################################################################################## */
    /* ============================================================================================== */
    /*  로그처리                                                                                       */
    /* ============================================================================================== */
    RPLS_ADM.RPL_PROG_LOG(V_REV_NO||'-'||VI_PLN_REV||'-'||VI_CUM_GUBUN, V_PLN_DT, 'RPO_MFG_YIELD_TABLE', 'RPO_MFG_YIELD_SP', 'E', 'WORK_END');
    --DBMS_OUTPUT.PUT_LINE('**********[ SUCCESS ] **********'||'-'|| TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS'));

    VI_RETURN_VALUE := 'SUCCESS';                                                                            /* END LOG [필수] */
    COMMIT;

    RETURN;

EXCEPTION                                                                                                    /* EXCEPTION  [필수] */
    WHEN NO_DATA_FOUND THEN
        RPLS_ADM.RPL_PROG_LOG(V_REV_NO||'-'||VI_PLN_REV||'-'||VI_CUM_GUBUN, V_PLN_DT, 'RPO_MFG_YIELD_TABLE', 'RPO_MFG_YIELD_SP', 'F', SUBSTR(SQLERRM, 1, 200));
        VI_RETURN_VALUE := 'PROCEDURE_ID : RPLS_ADM.RPO_MFG_YIELD_SP => EXCEPTION : NO_DATA_FOUND -> '||'ERR_CODE : '||SQLCODE||' ERR_MSG : '||SUBSTR(SQLERRM, 1, 200) ;
        ROLLBACK;
        RETURN;
    WHEN TOO_MANY_ROWS THEN
        RPLS_ADM.RPL_PROG_LOG(V_REV_NO||'-'||VI_PLN_REV||'-'||VI_CUM_GUBUN, V_PLN_DT, 'RPO_MFG_YIELD_TABLE', 'RPO_MFG_YIELD_SP', 'F', SUBSTR(SQLERRM, 1, 200));
        VI_RETURN_VALUE := 'PROCEDURE_ID : RPLS_ADM.RPO_MFG_YIELD_SP => EXCEPTION : TOO_MANY_ROWS -> '||'ERR_CODE : '||SQLCODE||' ERR_MSG : '||SUBSTR(SQLERRM, 1, 200) ;
        ROLLBACK;
        RETURN;
    WHEN INVALID_CURSOR THEN
        RPLS_ADM.RPL_PROG_LOG(V_REV_NO||'-'||VI_PLN_REV||'-'||VI_CUM_GUBUN, V_PLN_DT, 'RPO_MFG_YIELD_TABLE', 'RPO_MFG_YIELD_SP', 'F', SUBSTR(SQLERRM, 1, 200));
        VI_RETURN_VALUE := 'PROCEDURE_ID : RPLS_ADM.RPO_MFG_YIELD_SP => EXCEPTION : INVALID_CURSOR -> '||'ERR_CODE : '||SQLCODE||' ERR_MSG : '||SUBSTR(SQLERRM, 1, 200) ;
        ROLLBACK;
        RETURN;
    WHEN CURSOR_ALREADY_OPEN THEN
        RPLS_ADM.RPL_PROG_LOG(V_REV_NO||'-'||VI_PLN_REV||'-'||VI_CUM_GUBUN, V_PLN_DT, 'RPO_MFG_YIELD_TABLE', 'RPO_MFG_YIELD_SP', 'F', SUBSTR(SQLERRM, 1, 200));
        VI_RETURN_VALUE := 'PROCEDURE_ID : RPLS_ADM.RPO_MFG_YIELD_SP => EXCEPTION : CURSOR_ALREADY_OPEN -> '||'ERR_CODE : '||SQLCODE||' ERR_MSG : '||SUBSTR(SQLERRM, 1, 200) ;
        ROLLBACK;
        RETURN;
    WHEN ZERO_DIVIDE THEN
        RPLS_ADM.RPL_PROG_LOG(V_REV_NO||'-'||VI_PLN_REV||'-'||VI_CUM_GUBUN, V_PLN_DT, 'RPO_MFG_YIELD_TABLE', 'RPO_MFG_YIELD_SP', 'F', SUBSTR(SQLERRM, 1, 200));
        VI_RETURN_VALUE := 'PROCEDURE_ID : RPLS_ADM.RPO_MFG_YIELD_SP => EXCEPTION : ZERO_DIVIDE -> '||'ERR_CODE : '||SQLCODE||' ERR_MSG : '||SUBSTR(SQLERRM, 1, 200) ;
        ROLLBACK;
        RETURN;
    WHEN DUP_VAL_ON_INDEX THEN
        RPLS_ADM.RPL_PROG_LOG(V_REV_NO||'-'||VI_PLN_REV||'-'||VI_CUM_GUBUN, V_PLN_DT, 'RPO_MFG_YIELD_TABLE', 'RPO_MFG_YIELD_SP', 'F', SUBSTR(SQLERRM, 1, 200));
        VI_RETURN_VALUE := 'PROCEDURE_ID : RPLS_ADM.RPO_MFG_YIELD_SP => EXCEPTION : DUP_VAL_ON_INDEX -> '||'ERR_CODE : '||SQLCODE||' ERR_MSG : '||SUBSTR(SQLERRM, 1, 200) ;
        ROLLBACK;
        RETURN;
    WHEN INVALID_NUMBER THEN
        RPLS_ADM.RPL_PROG_LOG(V_REV_NO||'-'||VI_PLN_REV||'-'||VI_CUM_GUBUN, V_PLN_DT, 'RPO_MFG_YIELD_TABLE', 'RPO_MFG_YIELD_SP', 'F', SUBSTR(SQLERRM, 1, 200));
        VI_RETURN_VALUE := 'PROCEDURE_ID : RPLS_ADM.RPO_MFG_YIELD_SP => EXCEPTION : INVALID_NUMBER -> '||'ERR_CODE : '||SQLCODE||' ERR_MSG : '||SUBSTR(SQLERRM, 1, 200) ;
        ROLLBACK;
        RETURN;
    WHEN NOT_LOGGED_ON THEN
        RPLS_ADM.RPL_PROG_LOG(V_REV_NO||'-'||VI_PLN_REV||'-'||VI_CUM_GUBUN, V_PLN_DT, 'RPO_MFG_YIELD_TABLE', 'RPO_MFG_YIELD_SP', 'F', SUBSTR(SQLERRM, 1, 200));
        VI_RETURN_VALUE := 'PROCEDURE_ID : RPLS_ADM.RPO_MFG_YIELD_SP => EXCEPTION : NOT_LOGGED_ON -> '||'ERR_CODE : '||SQLCODE||' ERR_MSG : '||SUBSTR(SQLERRM, 1, 200) ;
        ROLLBACK;
        RETURN;
    WHEN TIMEOUT_ON_RESOURCE THEN
        RPLS_ADM.RPL_PROG_LOG(V_REV_NO||'-'||VI_PLN_REV||'-'||VI_CUM_GUBUN, V_PLN_DT, 'RPO_MFG_YIELD_TABLE', 'RPO_MFG_YIELD_SP', 'F', SUBSTR(SQLERRM, 1, 200));
        VI_RETURN_VALUE := 'PROCEDURE_ID : RPLS_ADM.RPO_MFG_YIELD_SP => EXCEPTION : TIMEOUT_ON_RESOURCE -> '||'ERR_CODE : '||SQLCODE||' ERR_MSG : '||SUBSTR(SQLERRM, 1, 200) ;
        ROLLBACK;
        RETURN;
    WHEN OTHERS  THEN
        RPLS_ADM.RPL_PROG_LOG(V_REV_NO||'-'||VI_PLN_REV||'-'||VI_CUM_GUBUN, V_PLN_DT, 'RPO_MFG_YIELD_TABLE', 'RPO_MFG_YIELD_SP', 'F', SUBSTR(SQLERRM, 1, 200));
        VI_RETURN_VALUE := 'PROCEDURE_ID : RPLS_ADM.RPO_MFG_YIELD_SP => EXCEPTION : OTHERS -> '||'ERR_CODE : '||SQLCODE||' ERR_MSG : '||SUBSTR(SQLERRM, 1, 200) ;
        ROLLBACK;
        RETURN;
END;


