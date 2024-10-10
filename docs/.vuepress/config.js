const {
    description
} = require('../package')

module.exports = {
    title: 'OpenCore Legacy Patcher',
    head: [
        ['meta', {
            name: 'theme-color',
            content: '#3eaf7c'
        }],
        ['meta', {
            name: 'apple-mobile-web-app-capable',
            content: 'yes'
        }],
        ['meta', {
            name: 'apple-mobile-web-app-status-bar-style',
            content: 'black'
        }],
        ["link", {
            rel: "'stylesheet",
            href: "/styles/website.css"
        },]
    ],
    base: '/OpenCore-Legacy-Patcher/',

    watch: {
        $page(newPage, oldPage) {
            if (newPage.key !== oldPage.key) {
                requestAnimationFrame(() => {
                    if (this.$route.hash) {
                        const element = document.getElementById(this.$route.hash.slice(1));

                        if (element && element.scrollIntoView) {
                            element.scrollIntoView();
                        }
                    }
                });
            }
        }
    },

    markdown: {
        extendMarkdown: md => {
            md.use(require('markdown-it-multimd-table'), {
                rowspan: true,
            });
        }
    },

    theme: 'vuepress-theme-succinct',
    globalUIComponents: [
        'ThemeManager'
    ],

    themeConfig: {
        lastUpdated: true,
        repo: 'https://github.com/dortania/OpenCore-Legacy-Patcher/',
        docsDir: 'docs',
        docsBranch: 'main',
        editLinks: true,
        editLinkText: 'Help us improve this page!',
        logo: 'homepage.png',

        sidebar: [{
            title: 'Introduction',
            collapsable: false,
            sidebarDepth: 1,
            children: [
                'START',
                'MODELS',
                'FAQ',
            ]

        },
        {
            title: 'How to install',
            collapsable: false,
            sidebarDepth: 1,
            children: [
                'INSTALLER',
                'BUILD',                
		'BOOT',
                'POST-INSTALL',
            ]

        },
        {
            title: 'macOS Support',
            collapsable: false,
            sidebarDepth: 1,
            children: [
                'SEQUOIA-DROP',
		'SONOMA-DROP',
		'VENTURA-DROP',
		'MONTEREY-DROP',
            ]
        },
 {
            title: 'Application',
            collapsable: false,
            sidebarDepth: 1,
            children: [
                'UPDATE',
                'UNINSTALL',
                'PROCESS',
            ]
        },
	{
            title: 'Troubleshooting',
            collapsable: false,
            sidebarDepth: 1,
            children: [
		'TROUBLESHOOTING',
                'ACCEL',
		'DEBUG',
                
            ]
        },	  
        {
            title: 'Misc',
            collapsable: false,
            sidebarDepth: 1,
            children: [
		'TIMEMACHINE',
                'ICNS',
                'WINDOWS',
                'UNIVERSALCONTROL',
            ]
        },
        {
            title: 'Credit',
            collapsable: false,
            sidebarDepth: 1,
            children: [
                'DONATE',
                'LICENSE',
            ]

        },
        {
            title: 'Documentation',
            collapsable: false,
            sidebarDepth: 1,
            children: [
                'ISSUES-HOLD',
                'TERMS',
                'HOW',
                'PATCHEXPLAIN',
            ]

        },
        ],
    },
    plugins: [
        '@vuepress/back-to-top',
        'vuepress-plugin-smooth-scroll',
        'vuepress-plugin-fulltext-search',
        ['@vuepress/medium-zoom',
            {
                selector: ".theme-succinct-content :not(a) > img",
                options: {
                    background: 'var(--bodyBgColor)'
                }
            }],
    ]
}
