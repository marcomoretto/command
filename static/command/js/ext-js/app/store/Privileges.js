Ext.define('command.store.Privileges', {
    extend: 'Ext.data.TreeStore',

    alias: 'store.script_tree',

    model: 'command.model.Privileges',

    proxy: {
        type: 'memory',
        reader: {
            type: 'json'
        }
    },

    root: {
        text: 'root',
        leaf: false
    },

    rootVisible: false
});
