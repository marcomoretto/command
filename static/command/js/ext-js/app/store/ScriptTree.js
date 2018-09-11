Ext.define('command.store.ScriptTree', {
    extend: 'Ext.data.TreeStore',

    alias: 'store.script_tree',

    model: 'command.model.ScriptTree',

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
