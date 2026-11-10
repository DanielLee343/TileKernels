from verify_inventory import check_parser_health
base={'target_id':'starter/hash-03','remote_detail_path':'/capture/attempt-001/detail','per_core_requested_bytes_status':'pending'}
sweep={'flagged':[{'target':'starter/hash-03','path':'/capture/attempt-001/detail/profile.log','errors':['droppedRecord=9']}],'missing':[]}
index={'cases':[{'target':'starter/hash-03','raw_dir':'/capture/attempt-001/detail'}]}
check_parser_health([base],sweep,index)
try:check_parser_health([base|{'per_core_requested_bytes_status':'new_dbi_audited_alarm'}],sweep,index)
except AssertionError:pass
else:raise AssertionError('flagged selected capture was admitted')
check_parser_health([base|{'remote_detail_path':'/capture/attempt-002/detail','per_core_requested_bytes_status':'new_dbi_audited_alarm'}],sweep,index)
sweep={'flagged':[],'missing':[['starter/hash-03','no parser summary']]}
try:check_parser_health([base|{'per_core_requested_bytes_status':'new_dbi_audited_alarm'}],sweep,index)
except AssertionError:pass
else:raise AssertionError('missing summary selected capture was admitted')
print('PASS parser gate catches flagged and missing selected captures')
