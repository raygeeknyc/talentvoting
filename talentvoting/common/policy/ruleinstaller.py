from typing import List

POLICY_RULE_NAME="eligible_votes_rules"

"""
Dyanamic function installer for policy rules functions.

Usage of function installer
rule_function='  print(a)\n  if a>b:\n    print("a")\n:  else:\n    print("b")'
update_eligible_votes=install_policy_engine_rules(rule_function,['a','b'])
update_eligible_votes(1,2)
  b

"""
def install_policy_engine_rules(function_body, arg_list:List[str]=[""], 
    function_name:str=POLICY_RULE_NAME)->function:
    """
    install_policy_engine_rules(function_body, arg_list, function_name)
    Creates a policy rules validation function from the function_body
    with the arg_list parameters

    Args:
        function_body: A string containing the function body,
          indented as needed.
        arg_list: Parameter names that are referenced in the func_body.
        function_name: The name to assign to the created function.

    Returns:
        The created function object, assign for later invocation.
    """
    function_string = (
        f"def {function_name}({','.join(arg_list)}):\n{function_body}"
        )
    loc = {}
    exec(function_string, globals(), loc)
    return loc[function_name]