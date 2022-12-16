-- Function / Procedure
-- a. Update PCR_res = T and PCR_ct = null for patient admission date after 1/9/2020
UPDATE test_info
SET PCR_res = 'T',
    PCR_ct =  NULL
WHERE patient_id IN (SELECT patient_id FROM patient_admission_date WHERE a_date >= '2021-9-1'); -- use 2021 because no one in db is before the required date

-- b. Read patient named 'Nguyen Van A' information
SELECT p.*, pad.addresses, pph.phones, pcm.comorbidities, pst.symptoms, pam.a_dates AS admission_dates, pdc.d_dates AS discharge_dates, ppl.prev_locations
FROM patient p

LEFT OUTER JOIN (
    SELECT patient_id, LISTAGG(p_address, ',') WITHIN GROUP (ORDER BY p_address) AS addresses
    FROM patient_address
    GROUP BY patient_id
    ) pad ON p.id = pad.patient_id
LEFT OUTER JOIN (
    SELECT patient_id, LISTAGG(phone_no, ',') WITHIN GROUP (ORDER BY phone_no) AS phones
    FROM patient_phone
    GROUP BY patient_id
    ) pph ON p.id = pph.patient_id
LEFT OUTER JOIN (
    SELECT patient_id, LISTAGG(comorbidity, ',') WITHIN GROUP (ORDER BY comorbidity) AS comorbidities
    FROM patient_comorbidity
    GROUP BY patient_id
    ) pcm ON p.id = pcm.patient_id
LEFT OUTER JOIN (
    SELECT patient_id, LISTAGG(symptom, ',') WITHIN GROUP (ORDER BY symptom) AS symptoms
    FROM patient_symptom
    GROUP BY patient_id
    ) pst ON p.id = pst.patient_id
LEFT OUTER JOIN (
    SELECT patient_id, LISTAGG(a_date, ',') WITHIN GROUP (ORDER BY a_date) AS a_dates
    FROM patient_admission_date
    GROUP BY patient_id
    ) pam ON p.id = pam.patient_id
LEFT OUTER JOIN (
    SELECT patient_id, LISTAGG(d_date, ',') WITHIN GROUP (ORDER BY d_date) AS d_dates
    FROM patient_discharge_date
    GROUP BY patient_id
    ) pdc ON p.id = pdc.patient_id
LEFT OUTER JOIN (
    SELECT patient_id, LISTAGG(prev_location, ',') WITHIN GROUP (ORDER BY prev_location) AS prev_locations
    FROM patient_prev_location
    GROUP BY patient_id
    ) ppl ON p.id = ppl.patient_id

WHERE first_name = 'A' and last_name = 'Nguyen Van'
;

-- c. Function to get patient test_info
CREATE OR REPLACE FUNCTION get_detail_patient
(id IN test_info.patient_id%TYPE)
RETURN SYS_REFCURSOR
AS
   o_cursor   SYS_REFCURSOR;
BEGIN
    OPEN o_cursor FOR
        SELECT *
        FROM test_info
        WHERE test_info.patient_id = id;
    RETURN o_cursor;
END 
;
-- Calling function
SELECT get_detail_patient('PAT001') FROM DUAL;

-- d. Procedure to sort the nurses in decreasing number of patients he/she
--    takes care in a period of time
CREATE OR REPLACE PROCEDURE sort_nurse_desc
(s_date IN DATE, e_date IN DATE, cursorParam OUT SYS_REFCURSOR)
IS
BEGIN
    OPEN cursorParam FOR
        SELECT n.id nurse_id, NVL(ctk.num_patient, 0) num_patient
        FROM nurse n
        LEFT OUTER JOIN (
            SELECT p.caretaker_id, COUNT(p.caretaker_id) num_patient
            FROM patient p
            JOIN patient_admission_date pam ON p.id = pam.patient_id
            AND pam.a_date >= s_date
            LEFT OUTER JOIN patient_discharge_date pdc ON p.id = pdc.patient_id
            AND (pdc.d_date <= e_date OR pdc.d_date IS NULL)
            GROUP BY p.caretaker_id
            ) ctk ON n.id = ctk.caretaker_id
        ORDER BY num_patient DESC;
END 
;
-- Execute procedure
var c refcursor;
execute sort_nurse_desc('2020-1-1','2022-1-1',:c)
print c;
