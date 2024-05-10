DELIMITER $$

CREATE TRIGGER check_time_slot_conflict
BEFORE INSERT ON MatchSession
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT DEFAULT 0;

    SELECT COUNT(*) INTO conflict_count
    FROM MatchSession
    WHERE stadium_id = NEW.stadium_id
      AND date = NEW.date
      AND (
          NEW.time_slot = time_slot OR
          NEW.time_slot + 1 = time_slot OR
          time_slot + 1 = NEW.time_slot
      );

    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Time slot conflict detected for the same stadium and date.';
    END IF;
END$$

DELIMITER ;
