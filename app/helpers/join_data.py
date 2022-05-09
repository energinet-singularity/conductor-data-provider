# Generic modules
import logging

# Modules
import pandas as pd

# Initialize log
log = logging.getLogger(__name__)


def create_conductor_dataframe(conductor_data: pd.DataFrame,
                               dd20_to_scada_name: pd.DataFrame,
                               scada_mapping: pd.DataFrame) -> pd.DataFrame:
    """
    TODO: doc me
    """

    # constant (ud som inputs til funcion)
    MRIDMAP_DLR_ENABLED_COL_NM = 'DLR_ENABLED'
    LINE_EMSNAME_COL_NM = 'LINE_EMSNAME'
    # EXPECTED_NAME_COL_NM = 'ACLINE_EMSNAME_EXPECTED'
    EXPECTED_NAME_COL_NM = 'acline_name_translated'
    dd20_name_col_nm = "DD20 Name"
    scada_name_col_nm = "ETS Name"

    # append column with list mapped name based on expected name if is existing in list, else keep name.
    # Remove expected name column
    # TODO ali i try/except

    acline_namemap_dict = dd20_to_scada_name.set_index(dd20_name_col_nm).to_dict()[scada_name_col_nm]

    mapped_name_list = [acline_namemap_dict[x] if x in acline_namemap_dict else x
                        for x in conductor_data[EXPECTED_NAME_COL_NM]]
    conductor_data[LINE_EMSNAME_COL_NM] = mapped_name_list
    conductor_data = conductor_data.drop(columns=[EXPECTED_NAME_COL_NM])

    # TODO rename column instead or just keep translated name and make new column

    # extract lists of unique line names from conductor and scada dataframe
    # TODO: remove lines which are below 132 as DLR will not be enabled for them?
    # TODO: list(set(self.topics_consumed_list) - set(self.topics_produced_list)) or differnence instead of comprehensions?
    # TODO: names_not_in_gis = list(set(mrid_list).difference(translated_names))
    # TODO: found_lines = list(set(mrid_list).intersection(translated_names))
    lines_in_conductor_data = set(conductor_data[LINE_EMSNAME_COL_NM].to_list())
    lines_in_scada_data = set(scada_mapping[LINE_EMSNAME_COL_NM].to_list())

    # Create list of lines which have DLR enabled flag set True
    lines_dlr_enabled = scada_mapping.loc[scada_mapping[MRIDMAP_DLR_ENABLED_COL_NM], LINE_EMSNAME_COL_NM].to_list()

    # report line names which are in DD20, but not ETS as info
    lines_only_in_conductor_data = sorted([x for x in lines_in_conductor_data if x not in lines_in_scada_data])
    if lines_only_in_conductor_data:
        log.info(f"Line(s) with name(s): '{lines_only_in_conductor_data}' exists in conductor data but not in SCADA data.")

    # report line names which are in ETS, but not DD20 as info
    lines_only_in_scada_data = sorted([x for x in lines_in_scada_data if x not in lines_in_conductor_data])
    if lines_only_in_scada_data:
        log.info(f"Line(s) with name(s): '{lines_only_in_scada_data}' exists in SCADA data but not in conductor data.")

    # report lines for which DLR is enabled, but date is not availiable in DD20 as errors
    lines_dlr_enabled_data_missing = sorted([x for x in lines_dlr_enabled if x not in lines_in_conductor_data])
    if lines_dlr_enabled_data_missing:
        log.error(f"Line(s) with name(s): '{lines_dlr_enabled_data_missing}', are enabled for DLR but has no conductor data.")

    # Join two dataframes where emsname commen key
    # TODO: how to handle missing data? (dlr enabled but no conductor data)
    dlr_dataframe = scada_mapping.join(conductor_data.set_index(LINE_EMSNAME_COL_NM),
                                       on=LINE_EMSNAME_COL_NM,
                                       how='inner')

    # TODO: make mrid as index in dataframe?

    # force uppercase
    dlr_dataframe.columns = dlr_dataframe.columns.str.upper()

    return dlr_dataframe
