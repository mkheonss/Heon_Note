/* ###################################################################################### */
/* ###################################################################################### */
/*   계획(PLAN)																																					   */
/* ###################################################################################### */
/* ###################################################################################### */
/*
	안녕하세요.
	BW에서 보내드리는 계획 원가/손익 관련 메일입니다.
	(기간 :2023, 버전 :CC2)에 해당하는
	제품별 손익(계획) 및 제품별 원가(계획)데이터가 적재되었습니다.
	해당기간의 계획데이터를 SCM으로 전송하시기 바랍니다.
	감사합니다.
*/

/*
계획데이터 (기간 :2023, 버전 :CC2)  적재됬다고  알람 메일이 와서
관련 I/F 및   배치들을  실행하였으니   참조 바랍니다.

ERP_PROD_PRFLOS_PLN : ERP원가손익-제품별손익계획
ERP_PROD_COST_PLN: ERP원가손익-제품별원가계획
이어서 아래의  계획관련 배치 실행해서 관련 테이블 데이터 입력 확인 했습니다.
*/

--===============================================
-- 계획관련 배치 실행해서 관련 테이블 데이터 입력 확인 했습니다.
--===============================================
/* COGS 계획 (input RPO_ERP_PROD_PROFLOS) */
EXECUTE RPO_ERP_PROD_PROFLOS_PLN_SP ('2023', 'CC2');		-- =>RPO_ERP_PROD_PROFLOS

/* COM 계획 (input  RPO_ERP_COMFG_FAB, ) */
EXECUTE RPO_ERP_COMFG_FAB_PLN_SP ('2023', 'CC2'); 			-- => RPO_ERP_COMFG_FAB
EXECUTE RPO_ERP_COMFG_PROD_PLN_SP ('2023', 'CC2'); 			-- => RPO_ERP_COMFG_PROD


/* ========== */
/*  확인 		   */
/* ========== */
SELECT *
  FROM RPO_ERP_PROD_PROFLOS
 WHERE 1 = 1
   AND COST_PLN_YY = '2023'
   AND VER_CD = 'CC2'
;


SELECT *
  FROM RPO_ERP_COMFG_FAB
 WHERE 1 = 1
   AND COST_PLN_YY = '2023'
   AND VER_CD = 'CC2'
;


SELECT *
  FROM RPO_ERP_COMFG_PROD
 WHERE 1 = 1
   AND COST_PLN_YY = '2023'
   AND VER_CD = 'CC2'
;


-- #################################################################################
--  2024.03.28 작업진행함.
-- #################################################################################

-- #################################################################################
--  2024 , D11
-- #################################################################################
--=================
--1. 확인      
--=================
select  *    FROM MAD_GTS WHERE GTS_TYP_CD = 'FIN_CONF_REV'		
     AND GTS_GVAL8 = '2024'		
     AND GTS_GVAL9 = 'D11'		
;

--=================
--2. VIEW 정보 변경
--=================
CREATE OR REPLACE FORCE VIEW RPLS_ADM.STI_PLN_COST_IF_VER_VW
( WORK_MM, WORK_WK_GBN, WORK_WK, I_PLAN_MM, 
  I_PLAN_VER, I_PLAN_WW )
AS
SELECT	'202401' AS WORK_MM
		    ,'W2' 		 AS WORK_WK_GBN
            ,'2' 		 AS WORK_WK
		    ,'202401' AS I_PLAN_MM
            ,'D11' 	 AS I_PLAN_VER    -- PRFLOS 2019 P10, P20, 2022 P20, Q20, S20, S30, S40 
            ,'W2' 		 AS I_PLAN_WW                 
  FROM	DUAL
;
--=================
--3. 배치실행
--=================
  --admin / nexcore
  --인스턴스 생성 / 인스턴스 실행 

--=================  
--4. 확인
--=================
select  * from  ERP_PROD_PRFLOS_PLN  order by crt_tm desc;
select  * from  ERP_PROD_COST_PLN  order by crt_tm desc;

--=================
-- 5. 배치실행
----===============
EXECUTE RPO_ERP_PROD_PROFLOS_PLN_SP ('2024', 'D11'); -- 계획년, 버전
EXECUTE RPO_ERP_COMFG_FAB_PLN_SP ('2024', 'D11'); -- 계획년, 버전
EXECUTE RPO_ERP_COMFG_PROD_PLN_SP ('2024', 'D11'); -- 계획년, 버전  

--=================
-- 6. 결과확인
----===============
SELECT  *  FROM RPO_ERP_PROD_PROFLOS
 WHERE 1=1
   AND COST_PLN_YY = '2024'
   AND VER_CD = 'D11'
   AND PLN_ACTOUT_GBN_CD = 'PLN'
; 
    
SELECT  *  FROM RPO_ERP_COMFG_FAB
 WHERE 1=1
   AND COST_PLN_YY = '2024'
   AND VER_CD = 'D11'
   AND PLN_ACTOUT_GBN_CD = 'PLN'
; 
    
SELECT  *  FROM RPO_ERP_COMFG_PROD
 WHERE 1=1
   AND COST_PLN_YY = '2024'
   AND VER_CD = 'D11'
   AND PLN_ACTOUT_GBN_CD = 'PLN'
;
 

-- #################################################################################
--  2024 , D21
-- #################################################################################
--=================
--1. 확인      
--=================
select  *    FROM MAD_GTS WHERE GTS_TYP_CD = 'FIN_CONF_REV'		
     AND GTS_GVAL8 = '2024'		
     AND GTS_GVAL9 = 'D21'		
;

--=================
--2. VIEW 정보 변경
--=================
CREATE OR REPLACE FORCE VIEW RPLS_ADM.STI_PLN_COST_IF_VER_VW
( WORK_MM, WORK_WK_GBN, WORK_WK, I_PLAN_MM, 
  I_PLAN_VER, I_PLAN_WW )
AS
SELECT	'202402' AS WORK_MM
		    ,'W2' 		 AS WORK_WK_GBN
            ,'2' 		 AS WORK_WK
		    ,'202402' AS I_PLAN_MM
            ,'D21' 	 AS I_PLAN_VER    -- PRFLOS 2019 P10, P20, 2022 P20, Q20, S20, S30, S40 
            ,'W2' 		 AS I_PLAN_WW                 
  FROM	DUAL
;
--=================
--3. 배치실행
--=================
  --admin / nexcore
  --인스턴스 생성 / 인스턴스 실행 

--=================  
--4. 확인
--=================
select  * from  ERP_PROD_PRFLOS_PLN  order by crt_tm desc;
select  * from  ERP_PROD_COST_PLN  order by crt_tm desc;

--=================
-- 5. 배치실행
----===============
EXECUTE RPO_ERP_PROD_PROFLOS_PLN_SP ('2024', 'D21'); -- 계획년, 버전
EXECUTE RPO_ERP_COMFG_FAB_PLN_SP ('2024', 'D21'); -- 계획년, 버전
EXECUTE RPO_ERP_COMFG_PROD_PLN_SP ('2024', 'D21'); -- 계획년, 버전  

--=================
-- 6. 결과확인
----===============
SELECT  *  FROM RPO_ERP_PROD_PROFLOS
 WHERE 1=1
   AND COST_PLN_YY = '2024'
   AND VER_CD = 'D21'
   AND PLN_ACTOUT_GBN_CD = 'PLN'
; 
    
SELECT  *  FROM RPO_ERP_COMFG_FAB
 WHERE 1=1
   AND COST_PLN_YY = '2024'
   AND VER_CD = 'D21'
   AND PLN_ACTOUT_GBN_CD = 'PLN'
; 
    
SELECT  *  FROM RPO_ERP_COMFG_PROD
 WHERE 1=1
   AND COST_PLN_YY = '2024'
   AND VER_CD = 'D21'
   AND PLN_ACTOUT_GBN_CD = 'PLN'
;
================================================================================


/* ###################################################################################### */
/* ###################################################################################### */
/*   실적(ACTOUT)																																					 */
/* ###################################################################################### */
/* ###################################################################################### */

/* ======================================================= */
/*
안녕하세요.
BW에서 보내드리는 수익성 실적 관련 메일입니다.
2024.01 기간에 해당하는
제품별 수익성 및 Wafer 수익성 데이터가 적재되었습니다.
해당기간의 실적데이터를 SCM으로 전송하시기 바랍니다.
감사합니다.
*/
/* ======================================================= */

/*
수고하십니다.
2024년 1월의 제품별 수익성 및 Wafer 수익성 실적 데이터가 적재되어서,
관련 IF 프로그램을 실행해서
아래의 테이블에  테이터를  IF했습니다.
ERP_PROD_PROFBLT_ACTOUT : ERP원가손익-제품별수익성실적
ERP_WF_PROFBLT_ACTOUT : ERP원가손익-Wafer수익성실적
*  이어서 아래의  실적관련 배치 실행을 완료했으니 참조 바랍니다.
*/
/* COGS 실적 */
EXECUTE RPO_ERP_PROD_PROFLOS_ACTOUT_SP ('202401');

/* COM 실적 */
EXECUTE RPO_ERP_COMFG_FAB_ACTOUT_SP ('202401');

EXECUTE RPO_ERP_COMFG_PROD_ACTOUT_SP ('202401');


/* ========== */
/*  확인 		   */
/* ========== */
SELECT *
  FROM RPO_ERP_PROD_PROFLOS
 WHERE 1 = 1
   AND TGT_YM = '202401'
;

SELECT *
  FROM RPO_ERP_COMFG_FAB
 WHERE 1 = 1
   AND TGT_YM = '202401'
;

SELECT *
  FROM RPO_ERP_COMFG_PROD
 WHERE 1 = 1
   AND TGT_YM = '202401'
;