CREATE OR REPLACE PROCEDURE RPLO_ADM1."RPO_EXP_WIP_PLAN_ASSIGN_CD_RP" (VI_PLANID IN VARCHAR2 DEFAULT NULL,VI_RETURN_VALUE IN OUT VARCHAR2)
AUTHID CURRENT_USER
IS
/*********************************************************************************
    -. PROGRAMMER  :
    -. CREATE_DATE :
    -. DESCRIPTION : Plan EXP_WIP_PLAN_ASSIGN_RP(대표코드) 을 등록한다.
    -. ARGUMENT    :
    -. HISTORY LOGIC
        MODIFIED DATE  MODIFIED   VERSION   DESCRIPTION
        2019-01-04                             Created this procedure.
    -. 20240925 PARTITION 관련 작업 추가(삭제,생성)

    -. IN TABLE    :
        RPLO_ADM1.O_WIP_PLAN_ASSIGN
    -. OUT TABLE   :
        RPLS_ADM.EXP_WIP_PLAN_ASSIGN_RP

********************************************************************************/

/*--- DEFINE VARIALBLE[OPTION]                                             ---*/

    V_PLN_DT       VARCHAR2(8);
    V_REV_NO       VARCHAR2(50);
    V_WORK_CNT     NUMBER;
    V_WORK_MM      VARCHAR2(8);
    V_PRE_WW       VARCHAR2(8);
    V_PLANID               VARCHAR2(100);          -- PLAN ID
    V_PLAN_TYPE            VARCHAR2(100);          -- PLAN TYPE
    V_COMMITCNT            INTEGER;                -- COMMIT COUNT
    V_PROGNAME             VARCHAR2(100);          -- PROGRAM NAME
    V_CURRJOB              VARCHAR2(100);          -- 현재 JOB
    V_TARGETTABLE          VARCHAR2(100);          -- Target Table
	
    V_PART_CHK             NUMBER;                 --PARTITION 작업 
    V_SQL                  CLOB;                   --PARTITION 작업 	
BEGIN

    DBMS_OUTPUT.ENABLE(9999999999);
    V_COMMITCNT := 10000;
    V_PROGNAME  := $$PLSQL_UNIT;
    V_TARGETTABLE := 'EXP_WIP_PLAN_ASSIGN_RP';

    SELECT TO_CHAR(SYSDATE,'YYYYMMDD'),'RPI_'||TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS')
    INTO V_PLN_DT,V_REV_NO
    FROM DUAL;

    COMMIT;

    IF VI_PLANID IS NOT NULL THEN
        SELECT PLANID
              ,PLAN_TYPE
        INTO   V_PLANID
              ,V_PLAN_TYPE
        FROM   RPLS_ADM.ODS_PLANMASTER_RP
        WHERE  PLANID = VI_PLANID;
    ELSE
        SELECT PLANID
              ,PLAN_TYPE
        INTO   V_PLANID
              ,V_PLAN_TYPE
        FROM   RPLS_ADM.ODS_PLANMASTER_RP
        WHERE  ACTIVE_FLAG = 'Y';
    END IF;

/*--- START LOG [필수]                                                     ---*/
    RPLS_ADM.RPL_PROG_LOG(V_PLANID, V_PLN_DT, V_TARGETTABLE, V_PROGNAME, 'S', 'NO_DESC');


    -- PROGRAM STATUS LOGGING - RUN
    RPLS_ADM.RPI_ODS_PLN_REV_STAT_RP(V_PLANID||'-R', V_PROGNAME, 'R');

/*******************************************************************************
    START MAIN LOGIC  [필수]
*******************************************************************************/

    --PARTITION 작업 START 

    SELECT COUNT(*)
      INTO V_PART_CHK
      FROM ALL_TAB_PARTITIONS
     WHERE 1=1
       AND TABLE_NAME     = 'EXP_WIP_PLAN_ASSIGN_RP'
       AND TABLE_OWNER    = 'RPLS_ADM'
       AND PARTITION_NAME = 'PART_'||V_PLANID||'-R'
    ;


     IF V_PART_CHK > 0 THEN   

        RPLS_ADM.RPO_TRUNC_EXP_AREA_PLAN_RP('EXP_WIP_PLAN_ASSIGN_RP',V_PLANID||'-R');   

        --DELETE  FROM RPLS_ADM.EXP_WIP_PLAN_ASSIGN_RP
        --WHERE   PLAN_NAME = V_PLANID ||'-R' ;
         
     ELSE   
         V_SQL := 'ALTER TABLE RPLS_ADM.EXP_WIP_PLAN_ASSIGN_RP ADD PARTITION "PART_'||V_PLANID||'-R" VALUES('''||V_PLANID||'-R'') TABLESPACE TS_RPLS_D001';       
         EXECUTE IMMEDIATE V_SQL;   
     END IF;   
     
     --PARTITION 작업 END 


    COMMIT;


    V_CURRJOB := 'EXP_WIP_PLAN_ASSIGN_RP 등록';

    INSERT INTO RPLS_ADM.EXP_WIP_PLAN_ASSIGN_RP
    (
        PLAN_NAME, DEMAND_NAME, DEMAND_LI_NAME,
        PKEY, TO_KEY, LOT_NO,
        ITEM_NAME, ITEM_NAME_M, FAB_ID, FCLTY_NAME, STEP_NUM,
        WIP_DTTM, WIP_QTY, SCLEVEL,
        STAGE, MATCH_CODE, CHIP_SEQ,
        CONSUME_DTTM, CONSUME_QTY, ENGINE_ID,
        PLANTYPE, PRODUCT_ID, ORG_PLAN_NAME,
        MODIFY_TYPE, MODIFY_DTTM, MODIFY_USER
    )
    SELECT  PLAN_NAME ||'-R' AS PLAN_NAME
           ,DEMAND_NAME
           ,DEMAND_LI_NAME
           ,PKEY, TO_KEY
           ,LOT_NO
           ,ITEM_NAME
           ,B.MAPITEM
           ,B.FAB_ID
           ,FCLTY_NAME
           ,STEP_NUM
           ,WIP_DTTM
           ,WIP_QTY
           ,A.SCLEVEL
           ,A.STAGE
           ,MATCH_CODE
           ,CHIP_SEQ
           ,CONSUME_DTTM
           ,CONSUME_QTY
           ,ENGINE_ID
           ,PLANTYPE
           ,PRODUCT_ID
           ,ORG_PLAN_NAME
           ,MODIFY_TYPE
           ,MODIFY_DTTM
           ,MODIFY_USER
    FROM    O_WIP_PLAN_ASSIGN A
           ,RPLS_ADM.ODS_ITEMSITE_RP B
    WHERE   A.PLAN_NAME     = V_PLANID
    AND     A.PLAN_NAME     = B.PLANID(+)
    AND     A.FCLTY_NAME    = B.SITEID(+)
    AND     A.ITEM_NAME     = B.ITEM(+)
    ;

    COMMIT;


    -- PROGRAM STATUS LOGGING - END
    RPLS_ADM.RPI_ODS_PLN_REV_STAT_RP(V_PLANID||'-R', V_PROGNAME, 'C');


/*--- MONITORING STORED PROCEDURE [필수]                                   ---*/
    RPLS_ADM.RPL_PROG_LOG(V_PLANID, V_PLN_DT, V_TARGETTABLE, V_PROGNAME, 'E', '#1-sp ');

/*--- END LOG [필수]                                                       ---*/
    RPLS_ADM.RPL_PROG_LOG(V_PLANID, V_PLN_DT, V_TARGETTABLE, V_PROGNAME, 'E', 'NO_DESC');

    VI_RETURN_VALUE := 'SUCCESS';
    RETURN;

/*--- EXCEPTION  [필수]                                                    ---*/
EXCEPTION
    WHEN OTHERS  THEN
        RPLS_ADM.RPL_PROG_LOG(V_PLANID, V_PLN_DT, V_TARGETTABLE, V_PROGNAME, 'F', SUBSTR(SQLERRM, 1, 200));
        DBMS_OUTPUT.PUT_LINE(SQLCODE|| ',' || SUBSTR(SQLERRM, 1, 200) );
        DBMS_OUTPUT.PUT_LINE(V_CURRJOB);
        VI_RETURN_VALUE := 'FAIL';

        -- PROGRAM STATUS LOGGING - FAIL
        RPLS_ADM.RPI_ODS_PLN_REV_STAT_RP(V_PLANID||'-R', V_PROGNAME, 'F');

        ROLLBACK;
        RETURN;
END;
/

