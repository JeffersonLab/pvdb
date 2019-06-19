from rcdb.model import ConditionType

class ParityConditions(object):
    """
    Default conditions are defined in rcdb
    Below are additional names for parity DB conditions
    """
    RUN_PRESTART_TIME = 'run_prestart_time'
    TOTAL_CHARGE = 'total_charge'
    BEAM_ENERGY = 'beam_energy'
    BEAM_CURRENT = 'beam_current'
    TARGET_TYPE = 'target_type'
    TARGET_ENCODER = 'target_encoder'
    TARGET_45ENCODER = 'target_45encoder'
    TARGET_90ENCODER = 'target_90encoder'
    IHWP = 'ihwp'
    RQWP = 'rqwp'
    VWIEN = 'vertical_wien'
    HWIEN = 'horizontal_wien'
    HELICITY_FREQUENCY = 'helicity_frequency'
    HELICITY_PATTERN = 'helicity_pattern'
    EXPERIMENT = 'experiment'
    RUN_FLAG = 'run_flag'
    WAC_COMMENT = 'wac_comment'

def create_condition_types(db):
    """
    Checks if condition types listed in class exist in the database and create them if not
    :param db: RCDBProvider connected to database
    :type db: RCDBProvider

    :return: None
    """

    all_types_dict = {t.name: t for t in db.get_condition_types()}

    def create_condition_type(name, value_type, description=""):
        all_types_dict[name] if name in all_types_dict.keys() \
            else db.create_condition_type(name, value_type, description)

    # create condition type
    create_condition_type(ParityConditions.RUN_PRESTART_TIME, ConditionType.TIME_FIELD, "coda prestart time")
    create_condition_type(ParityConditions.BEAM_ENERGY, ConditionType.FLOAT_FIELD, "GeV")
    create_condition_type(ParityConditions.BEAM_CURRENT, ConditionType.FLOAT_FIELD, "Average beam current in uA")
    create_condition_type(ParityConditions.TOTAL_CHARGE, ConditionType.FLOAT_FIELD)
    create_condition_type(ParityConditions.TARGET_TYPE, ConditionType.STRING_FIELD)
    create_condition_type(ParityConditions.TARGET_ENCODER, ConditionType.FLOAT_FIELD, "Target encoder position")
    create_condition_type(ParityConditions.TARGET_45ENCODER, ConditionType.FLOAT_FIELD, "Warm target encoder position")
    create_condition_type(ParityConditions.TARGET_90ENCODER, ConditionType.FLOAT_FIELD, "Cold target encoder position")
    create_condition_type(ParityConditions.IHWP, ConditionType.STRING_FIELD, "Insertable half-wave plate In/Out")
    create_condition_type(ParityConditions.RQWP, ConditionType.FLOAT_FIELD, "Rotating quarter wave plate")
    create_condition_type(ParityConditions.VWIEN, ConditionType.FLOAT_FIELD, "vertical wien angle in deg")
    create_condition_type(ParityConditions.HWIEN, ConditionType.FLOAT_FIELD, "horizontal wien angle in deg")
    create_condition_type(ParityConditions.HELICITY_PATTERN, ConditionType.STRING_FIELD, "helicity pattern")
    create_condition_type(ParityConditions.HELICITY_FREQUENCY, ConditionType.FLOAT_FIELD, "helicity board frequency in Hz")
    create_condition_type(ParityConditions.EXPERIMENT, ConditionType.STRING_FIELD, "experiment name")
    create_condition_type(ParityConditions.RUN_FLAG, ConditionType.STRING_FIELD, "Run flag filled by WAC (good, bad, suspicious)")
    create_condition_type(ParityConditions.WAC_COMMENT, ConditionType.STRING_FIELD, "additional comment for the run")
