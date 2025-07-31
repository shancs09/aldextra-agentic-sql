example_pairs=[
  {
    "question": "What workflows are in the multischedule group 'x'?",
    "sql": "SELECT DISTINCT spx.MULTIGRP.BEZ AS MultiGrpName, spx.WORKFLOWTYPE.BEZ AS WorkflowName FROM spx.MULTIGRP JOIN spx.MULTIGRP_WORKFLOWTYPES ON spx.MULTIGRP_WORKFLOWTYPES.MULTIGRP_F = spx.MULTIGRP.PRIMKEY JOIN spx.WORKFLOWTYPE ON spx.WORKFLOWTYPE.PRIMKEY = spx.MULTIGRP_WORKFLOWTYPES.WORKFLOWTYPE_F WHERE spx.MULTIGRP.BEZ = 'x'"
  },
  {
    "question": "Which role validates the workflow 'x'?",
    "sql": "SELECT DISTINCT spx.WORKFLOWTYPE.BEZ AS WorkflowName, spx.ROLLE.BEZ AS Rol FROM spx.WORKFLOWTYPE JOIN spx.MULTIGRP_WORKFLOWTYPES ON spx.WORKFLOWTYPE.PRIMKEY = spx.MULTIGRP_WORKFLOWTYPES.WORKFLOWTYPE_F JOIN spx.MULTIGRP_ROLLEN ON spx.MULTIGRP_WORKFLOWTYPES.MULTIGRP_F = spx.MULTIGRP_ROLLEN.MULTIGRP_F JOIN spx.ROLLE ON spx.MULTIGRP_ROLLEN.ROLLE_F = spx.ROLLE.PRIMKEY WHERE spx.WORKFLOWTYPE.BEZ = 'x'"
  },
  {
    "question": "In which multischedule groups has the worker with employee number 'x' ever been?",
    "sql": "SELECT DISTINCT spx.MULTIGRP.BEZ AS MultischeduleGroupName FROM spx.MITARBEITER JOIN spx.MONATSPLAN ON spx.MITARBEITER.NR = spx.MONATSPLAN.MANR_F JOIN spx.MP_MULTIGRP ON spx.MONATSPLAN.MANR_F = spx.MP_MULTIGRP.MANR_F JOIN spx.MULTIGRP ON spx.MP_MULTIGRP.MULTIGRP_F = spx.MULTIGRP.PRIMKEY WHERE spx.MITARBEITER.NR_X = 'x'"
  },
  {
    "question": "Who is the validator of the group 'x'?",
    "sql": "SELECT DISTINCT spx.ROLLE.BEZ AS Rol, spx.MITARBEITER.NACHNAME AS Name, spx.MITARBEITER.NR_X AS EmployeeID FROM spx.MULTIGRP_ROLLEN JOIN spx.ROLLE ON spx.MULTIGRP_ROLLEN.ROLLE_F = spx.ROLLE.PRIMKEY JOIN spx.MITARBEITER ON spx.MULTIGRP_ROLLEN.MA_F = spx.MITARBEITER.NR JOIN spx.MULTIGRP ON spx.MULTIGRP_ROLLEN.MULTIGRP_F = spx.MULTIGRP.PRIMKEY WHERE spx.MULTIGRP.BEZ = 'x'"
  },
  {
    "question": "Which employees are currently in the multischedule group 'x'?",
    "sql": "SELECT DISTINCT spx.MITARBEITER.NR_X AS EmployeeID FROM spx.MITARBEITER JOIN spx.MULTIGRP_MAS ON spx.MITARBEITER.NR = spx.MULTIGRP_MAS.MA_F JOIN spx.MULTIGRP ON spx.MULTIGRP_MAS.MULTIGRP_F = spx.MULTIGRP.PRIMKEY WHERE spx.MULTIGRP.BEZ = 'x' AND GETDATE() BETWEEN DATEADD(day, spx.MULTIGRP_MAS.VON, '1990-01-01') AND DATEADD(day, spx.MULTIGRP_MAS.BIS, '1990-01-01')"
  },
  {
    "question": "Which multischedule groups have the workflow 'x'?",
    "sql": "SELECT DISTINCT spx.MULTIGRP.BEZ AS MultischeduleGroupName FROM spx.MULTIGRP JOIN spx.MULTIGRP_WORKFLOWTYPES ON spx.MULTIGRP.PRIMKEY = spx.MULTIGRP_WORKFLOWTYPES.MULTIGRP_F JOIN spx.WORKFLOWTYPE ON spx.MULTIGRP_WORKFLOWTYPES.WORKFLOWTYPE_F = spx.WORKFLOWTYPE.PRIMKEY WHERE spx.WORKFLOWTYPE.BEZ = 'x' AND GETDATE() BETWEEN DATEADD(day, spx.MULTIGRP_WORKFLOWTYPES.VON, '1990-01-01') AND DATEADD(day, spx.MULTIGRP_WORKFLOWTYPES.BIS, '1990-01-01')"
  },
  {
    "question": "What shift did the employee 'x' have on 'yyyy-mm-dd'?",
    "sql": "SELECT DISTINCT spx.S_DIENST.SDIENST_KURZ AS ShiftName FROM spx.MITARBEITER JOIN spx.MONATSPLAN ON spx.MITARBEITER.NR = spx.MONATSPLAN.MANR_F JOIN spx.S_DIENST ON spx.MONATSPLAN.SD_FK = spx.S_DIENST.PRIMKEY WHERE spx.MITARBEITER.NR_X = 'x' AND spx.MONATSPLAN.TAG_F = DATEDIFF(day, '1990-01-01', 'yyyy-mm-dd')"
  },
  {
    "question": "How many employees, grouped by shift, work on 'yyyy-mm-dd' in the multischedule group 'x'?",
    "sql": "SELECT spx.S_DIENST.SDIENST_KURZ AS Shifts, COUNT(DISTINCT spx.MITARBEITER.NR_X) AS NumberOfEmployees FROM spx.MITARBEITER JOIN spx.MONATSPLAN ON spx.MITARBEITER.NR = spx.MONATSPLAN.MANR_F JOIN spx.MP_MULTIGRP ON spx.MONATSPLAN.MANR_F = spx.MP_MULTIGRP.MANR_F JOIN spx.MULTIGRP ON spx.MP_MULTIGRP.MULTIGRP_F = spx.MULTIGRP.PRIMKEY JOIN spx.S_DIENST ON spx.MONATSPLAN.SD_FK = spx.S_DIENST.PRIMKEY WHERE spx.MONATSPLAN.TAG_F = DATEDIFF(day, '1990-01-01', 'yyyy-mm-dd') AND spx.MULTIGRP.BEZ = 'x' GROUP BY spx.S_DIENST.SDIENST_KURZ"
  },
  {
    "question": "Which shifts use the account 'x' but do not use the account 'y'?",
    "sql": "SELECT DISTINCT spx.S_DIENST.SDIENST_KURZ AS Shifts FROM spx.S_DIENST JOIN spx.SDIENST_TT_KONTO ON spx.SDIENST_TT_KONTO.SD_FK = spx.S_DIENST.PRIMKEY WHERE spx.SDIENST_TT_KONTO.KONTOBEZ = 'x' AND NOT EXISTS (SELECT 1 FROM spx.SDIENST_TT_KONTO WHERE spx.SDIENST_TT_KONTO.SD_FK = spx.S_DIENST.PRIMKEY AND spx.SDIENST_TT_KONTO.KONTOBEZ = 'y')"
  },
  {
    "question": "Which shifts last 'x' minutes?",
    "sql": "SELECT DISTINCT spx.S_DIENST.SDIENST_KURZ AS Shift, spx.SDZATTZA.DAUER AS DurationInMinutes FROM spx.S_DIENST JOIN spx.SDZATTZA ON spx.S_DIENST.SDIENST_KURZ = spx.SDZATTZA.BEZ_F WHERE spx.SDZATTZA.DAUER = x"
  },
  {
    "question": "In which terminal did the employee with ID 'x' clock in on 'yyyy-mm-dd'?",
    "sql": "SELECT DISTINCT spx.ZEITBUCHUNG.TERMINALID AS Terminal, spx.ZEITBUCHUNG.ZER_F AS Event FROM spx.ZEITBUCHUNG JOIN spx.MITARBEITER ON spx.MITARBEITER.NR = spx.ZEITBUCHUNG.MANR_F WHERE spx.MITARBEITER.NR_X = 'x' AND spx.ZEITBUCHUNG.LDATUM = REPLACE('yyyy-mm-dd', '-', '') AND spx.ZEITBUCHUNG.ZER_F = 'Entrada'"
  },
  {
    "question": "Which roles approve the workflow 'x', including roles from any child multischedule groups recursively?",
    "sql": """
            WITH GroupHierarchy AS (
                SELECT PRIMKEY AS MULTIGRP_ID
                FROM spx.MULTIGRP
                WHERE BEZ = 'x'
                UNION ALL
                SELECT m.CHILD_MULTIGRP_F AS MULTIGRP_ID
                FROM spx.MULTIGRP_MULTIGRPS m
                JOIN GroupHierarchy gh ON gh.MULTIGRP_ID = m.MULTIGRP_F
            )
            SELECT DISTINCT
                r.BEZ AS RoleName
            FROM GroupHierarchy gh
            JOIN spx.MULTIGRP_ROLLEN mr ON mr.MULTIGRP_F = gh.MULTIGRP_ID
            JOIN spx.ROLLE r ON r.PRIMKEY = mr.ROLLE_F;
            """
  },
  {
    "question": "Do we have understaff of employees with the function 'x' on any multischedule group on 14th August 2019? I want a list of the understaffed groups with its needs and staff",
    "sql": """
            WITH NeedsData AS (
              SELECT
                spx.S_DIENST.SDIENST_KURZ AS Shifts,
                spx.BEST_SD.FKT_F AS Functions,
                SUM(spx.BEST_SD.SOLL_WERT) AS Needs
              FROM spx.BEST_SD
              JOIN spx.S_DIENST ON spx.S_DIENST.PRIMKEY = spx.BEST_SD.SD_FK
              WHERE spx.BEST_SD.TAGNR = DATEDIFF(day, '1990-01-01', '2019-08-14') AND spx.BEST_SD.FKT_F = 'x'
              GROUP BY spx.S_DIENST.SDIENST_KURZ, spx.BEST_SD.FKT_F

              UNION ALL

              SELECT
                spx.S_DIENST.SDIENST_KURZ AS Shifts,
                spx.SDMSM_TT.FKT_F AS Functions,
                SUM(spx.SDMSM_TT.SOLL_WERT) AS Needs
              FROM spx.SDMSM_TT
              JOIN spx.S_DIENST ON spx.S_DIENST.PRIMKEY = spx.SDMSM_TT.SD_FK
              JOIN spx.KALENDERTAG ON spx.KALENDERTAG.TTKURZ_F = spx.SDMSM_TT.TT_F
              WHERE spx.KALENDERTAG.KALENDERTAG = DATEDIFF(day, '1990-01-01', '2019-08-14') AND spx.SDMSM_TT.FKT_F = 'x'
              GROUP BY spx.S_DIENST.SDIENST_KURZ, spx.SDMSM_TT.FKT_F
            ),

            EmployeeData AS (
              SELECT
                spx.MULTIGRP.BEZ AS Groups,
                spx.S_DIENST.SDIENST_KURZ AS Shifts,
                spx.MONATSPLAN.FKT_F AS Functions,
                COUNT(spx.MITARBEITER.NR_X) AS Employees
              FROM spx.MITARBEITER
              JOIN spx.MONATSPLAN ON spx.MONATSPLAN.MANR_F = spx.MITARBEITER.NR
              JOIN spx.MP_MULTIGRP ON spx.MP_MULTIGRP.MANR_F = spx.MONATSPLAN.MANR_F
              JOIN spx.MULTIGRP ON spx.MULTIGRP.PRIMKEY = spx.MP_MULTIGRP.MULTIGRP_F
              JOIN spx.S_DIENST ON spx.MONATSPLAN.SD_FK = spx.S_DIENST.PRIMKEY
              WHERE spx.MONATSPLAN.TAG_F = DATEDIFF(day, '1990-01-01', '2019-08-14') AND spx.MONATSPLAN.FKT_F = 'x'
              GROUP BY spx.MULTIGRP.BEZ, spx.S_DIENST.SDIENST_KURZ, spx.MONATSPLAN.FKT_F
            )

            SELECT
              e.Groups,
              e.Shifts,
              e.Functions,
              n.Needs,
              e.Employees
            FROM EmployeeData e
            JOIN NeedsData n
              ON e.Shifts = n.Shifts AND e.Functions = n.Functions
            WHERE n.Needs > e.Employees
            ORDER BY e.Groups, e.Shifts
            """
  },
  {
    "question": "List all employees who have never been assigned to any multischedule group.",
    "sql": "SELECT spx.MITARBEITER.NR_X, spx.MITARBEITER.NACHNAME, spx.MITARBEITER.VORNAME FROM spx.MITARBEITER LEFT JOIN spx.MULTIGRP_MAS ON spx.MITARBEITER.NR = spx.MULTIGRP_MAS.MA_F WHERE spx.MULTIGRP_MAS.MA_F IS NULL;"
  },
  {
    "question": "To which multischedule group does employee with ID 'x' belong?",
    "sql": "SELECT DISTINCT spx.MITARBEITER.NR_X AS EmployeeID, spx.MITARBEITER.NACHNAME AS Name, spx.MP_MULTIGRP.MULTIGRP_F AS GrpMultiplanID, spx.MULTIGRP.BEZ AS NameGrpMultiplan FROM spx.MP_MULTIGRP JOIN spx.MITARBEITER ON spx.MP_MULTIGRP.MANR_F = spx.MITARBEITER.NR JOIN spx.MULTIGRP ON spx.MP_MULTIGRP.MULTIGRP_F = spx.MULTIGRP.PRIMKEY WHERE spx.MITARBEITER.NR_X = 'x'"
  },
  {
    "question": "I want a list of the original time stamps with the times, time events and employees’ ID on 'yyyy-mm-dd' before 'hh:mm', with no corrections",
    "sql": "SELECT DISTINCT spx.MITARBEITER.NR_X AS EmployeeID, spx.ZEITBUCHUNG.ORIG_ZEITSTEMPEL AS TimeSt, spx.ZEITBUCHUNG.ORIG_ZER_F AS TimeEvent FROM spx.ZEITBUCHUNG JOIN spx.MITARBEITER ON spx.MITARBEITER.NR = spx.ZEITBUCHUNG.MANR_F WHERE CAST(spx.ZEITBUCHUNG.ORIG_ZEITSTEMPEL AS DATE) = 'yyyy-mm-dd' AND CAST(spx.ZEITBUCHUNG.ORIG_ZEITSTEMPEL AS TIME) <= 'hh:mm' AND spx.ZEITBUCHUNG.ORIG_ZEITSTEMPEL = spx.ZEITBUCHUNG.ZEITSTEMPEL"
  },
  {
    "question": "How many employees with the function 'Auxiliar sanitario' do we need on 'yyyy-mm-dd'?",
    "sql": "SELECT DISTINCT spx.S_DIENST.SDIENST_KURZ AS Shifts, spx.BEST_SD.SOLL_WERT AS Needs, spx.BEST_SD.FKT_F AS Functions FROM spx.BEST_SD JOIN spx.S_DIENST ON spx.S_DIENST.PRIMKEY = spx.BEST_SD.SD_FK WHERE spx.BEST_SD.TAGNR = DATEDIFF(day, '1990-01-01', 'yyyy-mm-dd') + ' ' AND spx.BEST_SD.FKT_F = 'Auxiliar Sanitario' UNION ALL SELECT DISTINCT spx.S_DIENST.SDIENST_KURZ AS Shifts, spx.SDMSM_TT.SOLL_WERT AS Needs, spx.SDMSM_TT.FKT_F AS Functions FROM spx.SDMSM_TT JOIN spx.S_DIENST ON spx.S_DIENST.PRIMKEY = spx.SDMSM_TT.SD_FK JOIN spx.KALENDERTAG ON spx.KALENDERTAG.TTKURZ_F = spx.SDMSM_TT.TT_F WHERE spx.KALENDERTAG.KALENDERTAG = DATEDIFF(day, '1990-01-01', 'yyyy-mm-dd') + ' ' AND spx.SDMSM_TT.FKT_F = 'Auxiliar Sanitario'"
}]