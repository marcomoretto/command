Ext.define('command.view.welcome.Welcome', {
    extend: 'Ext.panel.Panel',
    title: 'Welcome',
    xtype: 'welcome',

    layout: 'fit',

    items: [{
        xtype: 'panel',
        margin: '10 500 30 100',
        html: '<h1>Hi there,</h1>' +
        '<h4>This is COMMAND (COMpendia MANagement Desktop) a web-based application used to download, collect ' +
        'and manage gene expression data from public databases.<br><br>' +
        'The GitHub repository is <a href="https://github.com/marcomoretto/command">here</a> while the documentation ' +
        'is hosted on <a href="https://command.readthedocs.io">ReadTheDocs</a>.<br><br>' +
        'You might want to start selecting a Compendium from the Option menu and then clicking on the Data ' +
        'Collection menu. <br><br>Live long and prosper!</h4>',
        layout: 'fit'
    }],

    initComponent: function() {
        this.callParent();
        mainTab = Ext.ComponentQuery.query('#main_tab_panel')[0];
        mainTab.setTitle('Welcome!');
    }
});