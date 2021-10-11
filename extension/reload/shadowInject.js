console.log('test');
const injectedScript = document.createElement('script');
injectedScript.src = chrome.extension.getURL('injected.js');
(document.head || document.documentElement).appendChild(injectedScript);