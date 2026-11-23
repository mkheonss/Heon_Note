/* Biz: gscm.r.pi.cot.cotb.db.DCOT999.S044 계획결과 Report-PLN_REV조회 */
/* IO: 곽명준,2020-07-23T16:45:23(곽명준,2020-07-08T16:49:31) */
/* ONLOAD_PLN_REV==>기준 PLN_REV */
WITH W_PLN_BASE AS
(
       /*RP계획*/
       SELECT PLN_REV
            , PLN_YM
            , PLN_WEEK_GBN_CD
            , PLN_TYP_CD
            , REV_NO
            , PLN_START_YM
            , PLN_END_YM
            , RLS_YN
            , SYNC_TYP_CD
            , PLN_NM
            , FINAL_CONF_TM
         FROM RPI_PLN_REV
        WHERE 1                            = 1
          AND RLS_YN                       = 'R'
          AND FINAL_CONF_TM      IS NOT NULL
          AND FINAL_CONF_USER_ID IS NOT NULL
              /*AND SYNC_TYP_CD = 'TGT'  SYNC_TYP_CD=PLN (RP계획), TGT (경영계획)*/
)
,
/* RP계획 START */
W_PLN AS
(
       SELECT ROWNUM AS RNUM
            , A.*
         FROM(
                     /* 1순위) 현재년도 중 최신 계획 년월 */
                     SELECT *
                       FROM(
                                       SELECT RANK() OVER(ORDER BY A.PLN_YM DESC, PLN_WEEK_GBN_CD DESC, PLN_REV DESC) AS RNK
                                            , A.*
                                         FROM W_PLN_BASE A
                                        WHERE 1 = 1
                                              /* AND A.SYNC_TYP_CD = 'TGT' */
                                              /* PLN (RP계획), TGT (경영계획) */
                                          AND SUBSTR(A.PLN_YM, 0, 4) = TO_CHAR(SYSDATE, 'YYYY')
                            )
                      WHERE RNK = 1

                     UNION ALL

                     /*     2순위) 1순위 만족하는 계획이 없을 경우 현재년도 무시하고 최신계획 년월     3순위) 1순위, 2순위를 만족하는 동일한 계획년월에 주차가 다른 계획이 있을 경우 FINAL_CONF_TM 이 나중인 계획을 최신계획으로 간주함.     */
                     SELECT *
                       FROM(
                                       SELECT RANK() OVER(ORDER BY A.PLN_YM DESC, A.FINAL_CONF_TM DESC) AS RNK
                                            , A.*
                                         FROM W_PLN_BASE A
                                        WHERE 1 = 1
                                              /* AND A.SYNC_TYP_CD = 'TGT' */
                                              /* PLN (RP계획), TGT (경영계획) */
                            )
                      WHERE RNK = 1
              )
              A
        WHERE 1       = 1
          AND ROWNUM <= 1
)
/* RP계획 END */
,
/* 비교 START */
W_PLN_VS AS
(
       /*    1순위) 사용자가 선택한 Plan Type의 선택값과 상관없이 항상 R/P계획과 경영계획 모두를 대상으로 함.    2순위) W_PLN 의 PLAN MONTH 값보다 작은 최신 계획년월    3순위) 2순위를 만족하는 계획년월의 PLAN REV 이 여러개 있을 경우에는 FINAL_CONF_TM 이 나중인 계획을 최신계획으로 간주함.    */
       SELECT *
         FROM(
                         SELECT RANK() OVER(ORDER BY A.PLN_YM DESC, A.FINAL_CONF_TM DESC) AS RNK
                              , A.*
                           FROM W_PLN_BASE A
                          WHERE TO_NUMBER(A.PLN_YM) =
                                (
                                       SELECT MAX(PLN_YM) AS PLN_YM
                                         FROM W_PLN_BASE A
                                        WHERE TO_NUMBER(A.PLN_YM) <
                                              (
                                                     SELECT TO_NUMBER(PLN_YM)
                                                       FROM W_PLN
                                              )
                                )
              )
)
/* 비교 END */
,
/* 경영계획 YEAR START */
W_TGT AS
(
       SELECT ROWNUM
            , A.*
         FROM(
                         SELECT RANK() OVER(ORDER BY PLN_YM DESC) AS RNK
                              , A.*
                           FROM W_PLN_BASE A
                          WHERE 1 = 1
                                /*AND SYNC_TYP_CD = 'TGT'*/
                            AND SUBSTR(PLN_YM, 0, 4) = SUBSTR(TO_CHAR(SYSDATE, 'YYYY'), 0, 4)

                       UNION ALL

                         SELECT RANK() OVER(ORDER BY PLN_YM DESC) AS RNK
                              , A.*
                           FROM W_PLN_BASE A
                          WHERE 1 = 1
                                /*AND SYNC_TYP_CD = 'TGT'*/
              )
              A
        WHERE ROWNUM<=1
)
SELECT A.RNK             AS A_RANK
     , A.PLN_REV         AS A_PLAN_REV
     , A.PLN_YM          AS A_PLN_YM
     , A.PLN_WEEK_GBN_CD AS A_PLN_WEEK_GBN_CD
     , A.PLN_TYP_CD      AS A_PLN_TYP_CD
     , A.REV_NO          AS A_REV_NO
     , A.PLN_START_YM    AS A_PLN_START_YM
     , A.PLN_END_YM      AS A_PLN_END_YM
     , A.RLS_YN          AS A_RLS_YN
     , A.SYNC_TYP_CD     AS A_SYNC_TYP_CD
     , A.PLN_NM          AS A_PLN_NM
     , B.RNK             AS B_RANK
     , B.PLN_REV         AS B_PLAN_REV
     , B.PLN_YM          AS B_PLN_YM
     , B.PLN_WEEK_GBN_CD AS B_PLN_WEEK_GBN_CD
     , B.PLN_TYP_CD      AS B_PLN_TYP_CD
     , B.REV_NO          AS B_REV_NO
     , B.PLN_START_YM    AS B_PLN_START_YM
     , B.PLN_END_YM      AS B_PLN_END_YM
     , B.RLS_YN          AS B_RLS_YN
     , B.SYNC_TYP_CD     AS B_SYNC_TYP_CD
     , B.PLN_NM          AS B_PLN_NM
     , C.RNK             AS C_RANK
     , C.PLN_REV         AS C_PLAN_REV
     , C.PLN_YM          AS C_PLN_YM
     , C.PLN_WEEK_GBN_CD AS C_PLN_WEEK_GBN_CD
     , C.PLN_TYP_CD      AS C_PLN_TYP_CD
     , C.REV_NO          AS C_REV_NO
     , C.PLN_START_YM    AS C_PLN_START_YM
     , C.PLN_END_YM      AS C_PLN_END_YM
     , C.RLS_YN          AS C_RLS_YN
     , C.SYNC_TYP_CD     AS C_SYNC_TYP_CD
     , C.PLN_NM          AS C_PLN_NM
     , A.PLN_YM          AS A_PLN_TGT_START_YM
     , SUBSTR(A.PLN_YM, 1, 4)
              || '01' AS SEARCH_START_YM
     , SUBSTR(A.PLN_YM, 1, 4)
              || '12' AS SEARCH_END_YM
     , SUBSTR(A.PLN_YM, 1, 4)
              || '01' AS ORG_SEARCH_START_YM
     , SUBSTR(A.PLN_YM, 1, 4)
              || '12'                                                       AS ORG_SEARCH_END_YM
     , TO_CHAR(ADD_MONTHS(TO_DATE(A.PLN_START_YM, 'YYYYMM'), -1), 'YYYYMM') AS A_PLN_START_YM_1
     , TO_CHAR(ADD_MONTHS(TO_DATE(B.PLN_START_YM, 'YYYYMM'), -1), 'YYYYMM') AS B_PLN_START_YM_1
  FROM W_PLN A
     , W_PLN_VS B
     , W_TGT C
;


SELECT * FROM USER_SOURCE WHERE TEXT LIKE '%RPO_SITE_LINE_MFG_PLN%'; --(프로시저,함수)



RPO_SITE_LINE_MFG_PLN_CODE_SP