const Configuration = {
    /*
     * Resolve and load @commitlint/config-conventional from node_modules.
     * Referenced packages must be installed
     */
    extends: ['@commitlint/config-conventional'],
    /*
     * Any rules defined here will override rules from @commitlint/config-conventional
     */
    rules: {
        'header-max-length': [2, 'always', 72],
        'subject-case': [2, 'always', 'sentence-case'],
        'scope-enum': [2, 'always'],
    },
};

module.exports = Configuration;
