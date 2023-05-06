class LSysConfigError(Exception):
    pass

class NoVariablesDefinedError(LSysConfigError):
    pass

class FixedAxiomError(LSysConfigError):
    pass

class VariableConstantOverlapError(LSysConfigError):
    pass

class AxiomWithUndefinedSymbolErrror(LSysConfigError):
    pass

class RuleVariableMismatchError(LSysConfigError):
    pass

class UndefinedSymbolInRuleOutputError(LSysConfigError):
    pass

class TranslationSymbolMismatchError(LSysConfigError):
    pass

class UnsupportedTranslationError(LSysConfigError):
    pass