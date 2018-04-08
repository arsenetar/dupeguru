/*
 * searchtools.js_t
 * ~~~~~~~~~~~~~~~~
 *
 * Sphinx JavaScript utilities for the full-text search.
 *
 * :copyright: Copyright 2007-2018 by the Sphinx team, see AUTHORS.
 * :license: BSD, see LICENSE for details.
 *
 */


/* Non-minified version JS is _stemmer.js if file is provided */ 
var JSX={};(function(l){function m(b,e){var a=function(){};a.prototype=e.prototype;var c=new a;for(var d in b){b[d].prototype=c}}function P(c,b){for(var a in b.prototype)if(b.prototype.hasOwnProperty(a))c.prototype[a]=b.prototype[a]}function g(a,b,d){function c(a,b,c){delete a[b];a[b]=c;return c}Object.defineProperty(a,b,{get:function(){return c(a,b,d())},set:function(d){c(a,b,d)},enumerable:true,configurable:true})}function O(a,b,c){return a[b]=a[b]/c|0}var u=parseInt;var v=parseFloat;function N(a){return a!==a}var x=isFinite;var y=encodeURIComponent;var z=decodeURIComponent;var A=encodeURI;var B=decodeURI;var C=Object.prototype.toString;var D=Object.prototype.hasOwnProperty;function k(){}l.require=function(b){var a=q[b];return a!==undefined?a:null};l.profilerIsRunning=function(){return k.getResults!=null};l.getProfileResults=function(){return(k.getResults||function(){return{}})()};l.postProfileResults=function(a,b){if(k.postResults==null)throw new Error('profiler has not been turned on');return k.postResults(a,b)};l.resetProfileResults=function(){if(k.resetResults==null)throw new Error('profiler has not been turned on');return k.resetResults()};l.DEBUG=false;function G(){};m([G],Error);function a(a,b,c){this.F=a.length;this.K=a;this.L=b;this.I=c;this.H=null;this.P=null};m([a],Object);function p(){};m([p],Object);function i(){var a;var b;var c;this.G={};a=this.E='';b=this._=0;c=this.A=a.length;this.B=0;this.D=b;this.C=c};m([i],p);function s(a,b){a.E=b.E;a._=b._;a.A=b.A;a.B=b.B;a.D=b.D;a.C=b.C};function e(b,d,c,e){var a;if(b._>=b.A){return false}a=b.E.charCodeAt(b._);if(a>e||a<c){return false}a-=c;if((d[a>>>3]&1<<(a&7))===0){return false}b._++;return true};function r(b,d,c,e){var a;if(b._<=b.B){return false}a=b.E.charCodeAt(b._-1);if(a>e||a<c){return false}a-=c;if((d[a>>>3]&1<<(a&7))===0){return false}b._--;return true};function o(a,d,c,e){var b;if(a._>=a.A){return false}b=a.E.charCodeAt(a._);if(b>e||b<c){a._++;return true}b-=c;if((d[b>>>3]&1<<(b&7))===0){a._++;return true}return false};function j(a,d,c,e){var b;if(a._<=a.B){return false}b=a.E.charCodeAt(a._-1);if(b>e||b<c){a._--;return true}b-=c;if((d[b>>>3]&1<<(b&7))===0){a._--;return true}return false};function h(a,b,d){var c;if(a.A-a._<b){return false}if(a.E.slice(c=a._,c+b)!==d){return false}a._+=b;return true};function d(a,b,d){var c;if(a._-a.B<b){return false}if(a.E.slice((c=a._)-b,c)!==d){return false}a._-=b;return true};function n(f,m,p){var b;var d;var e;var n;var g;var k;var l;var i;var h;var c;var a;var j;var o;b=0;d=p;e=f._;n=f.A;g=0;k=0;l=false;while(true){i=b+(d-b>>>1);h=0;c=g<k?g:k;a=m[i];for(j=c;j<a.F;j++){if(e+c===n){h=-1;break}h=f.E.charCodeAt(e+c)-a.K.charCodeAt(j);if(h!==0){break}c++}if(h<0){d=i;k=c}else{b=i;g=c}if(d-b<=1){if(b>0){break}if(d===b){break}if(l){break}l=true}}while(true){a=m[b];if(g>=a.F){f._=e+a.F|0;if(a.H==null){return a.I}o=a.H(a.P);f._=e+a.F|0;if(o){return a.I}}b=a.L;if(b<0){return 0}}return-1};function f(d,m,p){var b;var g;var e;var n;var f;var k;var l;var i;var h;var c;var a;var j;var o;b=0;g=p;e=d._;n=d.B;f=0;k=0;l=false;while(true){i=b+(g-b>>1);h=0;c=f<k?f:k;a=m[i];for(j=a.F-1-c;j>=0;j--){if(e-c===n){h=-1;break}h=d.E.charCodeAt(e-1-c)-a.K.charCodeAt(j);if(h!==0){break}c++}if(h<0){g=i;k=c}else{b=i;f=c}if(g-b<=1){if(b>0){break}if(g===b){break}if(l){break}l=true}}while(true){a=m[b];if(f>=a.F){d._=e-a.F|0;if(a.H==null){return a.I}o=a.H(d);d._=e-a.F|0;if(o){return a.I}}b=a.L;if(b<0){return 0}}return-1};function E(a,b,d,e){var c;c=e.length-(d-b);a.E=a.E.slice(0,b)+e+a.E.slice(d);a.A+=c|0;if(a._>=d){a._+=c|0}else if(a._>b){a._=b}return c|0};function c(a,f){var b;var c;var d;var e;b=false;if((c=a.D)<0||c>(d=a.C)||d>(e=a.A)||e>a.E.length?false:true){E(a,a.D,a.C,f);b=true}return b};i.prototype.J=function(){return false};i.prototype.c=function(b){var a;var c;var d;var e;a=this.G['.'+b];if(a==null){c=this.E=b;d=this._=0;e=this.A=c.length;this.B=0;this.D=d;this.C=e;this.J();a=this.E;this.G['.'+b]=a}return a};i.prototype.stemWord=i.prototype.c;i.prototype.d=function(e){var d;var b;var c;var a;var f;var g;var h;d=[];for(b=0;b<e.length;b++){c=e[b];a=this.G['.'+c];if(a==null){f=this.E=c;g=this._=0;h=this.A=f.length;this.B=0;this.D=g;this.C=h;this.J();a=this.E;this.G['.'+c]=a}d.push(a)}return d};i.prototype.stemWords=i.prototype.d;function b(){i.call(this);this.I_p2=0;this.I_p1=0;this.I_pV=0};m([b],i);b.prototype.M=function(a){this.I_p2=a.I_p2;this.I_p1=a.I_p1;this.I_pV=a.I_pV;s(this,a)};b.prototype.copy_from=b.prototype.M;b.prototype.W=function(){var p;var j;var f;var g;var i;var a;var d;var k;var l;var m;var n;var o;var q;a:while(true){p=this._;i=true;g:while(i===true){i=false;h:while(true){j=this._;a=true;b:while(a===true){a=false;d=true;c:while(d===true){d=false;f=this._;k=true;d:while(k===true){k=false;if(!e(this,b.g_v,97,251)){break d}this.D=this._;l=true;e:while(l===true){l=false;g=this._;m=true;f:while(m===true){m=false;if(!h(this,1,'u')){break f}this.C=this._;if(!e(this,b.g_v,97,251)){break f}if(!c(this,'U')){return false}break e}this._=g;n=true;f:while(n===true){n=false;if(!h(this,1,'i')){break f}this.C=this._;if(!e(this,b.g_v,97,251)){break f}if(!c(this,'I')){return false}break e}this._=g;if(!h(this,1,'y')){break d}this.C=this._;if(!c(this,'Y')){return false}}break c}this._=f;o=true;d:while(o===true){o=false;this.D=this._;if(!h(this,1,'y')){break d}this.C=this._;if(!e(this,b.g_v,97,251)){break d}if(!c(this,'Y')){return false}break c}this._=f;if(!h(this,1,'q')){break b}this.D=this._;if(!h(this,1,'u')){break b}this.C=this._;if(!c(this,'U')){return false}}this._=j;break h}q=this._=j;if(q>=this.A){break g}this._++}continue a}this._=p;break a}return true};b.prototype.r_prelude=b.prototype.W;function H(a){var q;var k;var f;var g;var i;var j;var d;var l;var m;var n;var o;var p;var r;a:while(true){q=a._;i=true;g:while(i===true){i=false;h:while(true){k=a._;j=true;b:while(j===true){j=false;d=true;c:while(d===true){d=false;f=a._;l=true;d:while(l===true){l=false;if(!e(a,b.g_v,97,251)){break d}a.D=a._;m=true;e:while(m===true){m=false;g=a._;n=true;f:while(n===true){n=false;if(!h(a,1,'u')){break f}a.C=a._;if(!e(a,b.g_v,97,251)){break f}if(!c(a,'U')){return false}break e}a._=g;o=true;f:while(o===true){o=false;if(!h(a,1,'i')){break f}a.C=a._;if(!e(a,b.g_v,97,251)){break f}if(!c(a,'I')){return false}break e}a._=g;if(!h(a,1,'y')){break d}a.C=a._;if(!c(a,'Y')){return false}}break c}a._=f;p=true;d:while(p===true){p=false;a.D=a._;if(!h(a,1,'y')){break d}a.C=a._;if(!e(a,b.g_v,97,251)){break d}if(!c(a,'Y')){return false}break c}a._=f;if(!h(a,1,'q')){break b}a.D=a._;if(!h(a,1,'u')){break b}a.C=a._;if(!c(a,'U')){return false}}a._=k;break h}r=a._=k;if(r>=a.A){break g}a._++}continue a}a._=q;break a}return true};b.prototype.U=function(){var t;var i;var r;var d;var f;var g;var h;var c;var a;var j;var k;var l;var m;var s;var p;var q;this.I_pV=p=this.A;this.I_p1=p;this.I_p2=p;t=this._;d=true;b:while(d===true){d=false;f=true;c:while(f===true){f=false;i=this._;g=true;a:while(g===true){g=false;if(!e(this,b.g_v,97,251)){break a}if(!e(this,b.g_v,97,251)){break a}if(this._>=this.A){break a}this._++;break c}this._=i;h=true;a:while(h===true){h=false;if(n(this,b.a_0,3)===0){break a}break c}s=this._=i;if(s>=this.A){break b}this._++;a:while(true){c=true;d:while(c===true){c=false;if(!e(this,b.g_v,97,251)){break d}break a}if(this._>=this.A){break b}this._++}}this.I_pV=this._}q=this._=t;r=q;a=true;a:while(a===true){a=false;c:while(true){j=true;b:while(j===true){j=false;if(!e(this,b.g_v,97,251)){break b}break c}if(this._>=this.A){break a}this._++}b:while(true){k=true;c:while(k===true){k=false;if(!o(this,b.g_v,97,251)){break c}break b}if(this._>=this.A){break a}this._++}this.I_p1=this._;b:while(true){l=true;c:while(l===true){l=false;if(!e(this,b.g_v,97,251)){break c}break b}if(this._>=this.A){break a}this._++}c:while(true){m=true;b:while(m===true){m=false;if(!o(this,b.g_v,97,251)){break b}break c}if(this._>=this.A){break a}this._++}this.I_p2=this._}this._=r;return true};b.prototype.r_mark_regions=b.prototype.U;function I(a){var s;var i;var r;var d;var f;var g;var h;var c;var j;var k;var l;var m;var p;var t;var q;var u;a.I_pV=q=a.A;a.I_p1=q;a.I_p2=q;s=a._;d=true;b:while(d===true){d=false;f=true;c:while(f===true){f=false;i=a._;g=true;a:while(g===true){g=false;if(!e(a,b.g_v,97,251)){break a}if(!e(a,b.g_v,97,251)){break a}if(a._>=a.A){break a}a._++;break c}a._=i;h=true;a:while(h===true){h=false;if(n(a,b.a_0,3)===0){break a}break c}t=a._=i;if(t>=a.A){break b}a._++;a:while(true){c=true;d:while(c===true){c=false;if(!e(a,b.g_v,97,251)){break d}break a}if(a._>=a.A){break b}a._++}}a.I_pV=a._}u=a._=s;r=u;j=true;a:while(j===true){j=false;c:while(true){k=true;b:while(k===true){k=false;if(!e(a,b.g_v,97,251)){break b}break c}if(a._>=a.A){break a}a._++}b:while(true){l=true;c:while(l===true){l=false;if(!o(a,b.g_v,97,251)){break c}break b}if(a._>=a.A){break a}a._++}a.I_p1=a._;b:while(true){m=true;c:while(m===true){m=false;if(!e(a,b.g_v,97,251)){break c}break b}if(a._>=a.A){break a}a._++}c:while(true){p=true;b:while(p===true){p=false;if(!o(a,b.g_v,97,251)){break b}break c}if(a._>=a.A){break a}a._++}a.I_p2=a._}a._=r;return true};b.prototype.V=function(){var a;var e;var d;b:while(true){e=this._;d=true;a:while(d===true){d=false;this.D=this._;a=n(this,b.a_1,4);if(a===0){break a}this.C=this._;switch(a){case 0:break a;case 1:if(!c(this,'i')){return false}break;case 2:if(!c(this,'u')){return false}break;case 3:if(!c(this,'y')){return false}break;case 4:if(this._>=this.A){break a}this._++;break}continue b}this._=e;break b}return true};b.prototype.r_postlude=b.prototype.V;function J(a){var d;var f;var e;b:while(true){f=a._;e=true;a:while(e===true){e=false;a.D=a._;d=n(a,b.a_1,4);if(d===0){break a}a.C=a._;switch(d){case 0:break a;case 1:if(!c(a,'i')){return false}break;case 2:if(!c(a,'u')){return false}break;case 3:if(!c(a,'y')){return false}break;case 4:if(a._>=a.A){break a}a._++;break}continue b}a._=f;break b}return true};b.prototype.S=function(){return!(this.I_pV<=this._)?false:true};b.prototype.r_RV=b.prototype.S;b.prototype.Q=function(){return!(this.I_p1<=this._)?false:true};b.prototype.r_R1=b.prototype.Q;b.prototype.R=function(){return!(this.I_p2<=this._)?false:true};b.prototype.r_R2=b.prototype.R;b.prototype.Y=function(){var a;var E;var H;var e;var D;var g;var F;var G;var h;var I;var A;var B;var p;var k;var l;var m;var n;var o;var i;var q;var s;var t;var u;var v;var w;var x;var y;var z;var J;var K;var L;var C;this.C=this._;a=f(this,b.a_4,43);if(a===0){return false}this.D=this._;switch(a){case 0:return false;case 1:if(!(!(this.I_p2<=this._)?false:true)){return false}if(!c(this,'')){return false}break;case 2:if(!(!(this.I_p2<=this._)?false:true)){return false}if(!c(this,'')){return false}E=this.A-this._;p=true;c:while(p===true){p=false;this.C=this._;if(!d(this,2,'ic')){this._=this.A-E;break c}this.D=this._;k=true;b:while(k===true){k=false;H=this.A-this._;l=true;a:while(l===true){l=false;if(!(!(this.I_p2<=this._)?false:true)){break a}if(!c(this,'')){return false}break b}this._=this.A-H;if(!c(this,'iqU')){return false}}}break;case 3:if(!(!(this.I_p2<=this._)?false:true)){return false}if(!c(this,'log')){return false}break;case 4:if(!(!(this.I_p2<=this._)?false:true)){return false}if(!c(this,'u')){return false}break;case 5:if(!(!(this.I_p2<=this._)?false:true)){return false}if(!c(this,'ent')){return false}break;case 6:if(!(!(this.I_pV<=this._)?false:true)){return false}if(!c(this,'')){return false}e=this.A-this._;m=true;a:while(m===true){m=false;this.C=this._;a=f(this,b.a_2,6);if(a===0){this._=this.A-e;break a}this.D=this._;switch(a){case 0:this._=this.A-e;break a;case 1:if(!(!(this.I_p2<=this._)?false:true)){this._=this.A-e;break a}if(!c(this,'')){return false}this.C=this._;if(!d(this,2,'at')){this._=this.A-e;break a}this.D=J=this._;if(!(!(this.I_p2<=J)?false:true)){this._=this.A-e;break a}if(!c(this,'')){return false}break;case 2:n=true;b:while(n===true){n=false;D=this.A-this._;o=true;c:while(o===true){o=false;if(!(!(this.I_p2<=this._)?false:true)){break c}if(!c(this,'')){return false}break b}K=this._=this.A-D;if(!(!(this.I_p1<=K)?false:true)){this._=this.A-e;break a}if(!c(this,'eux')){return false}}break;case 3:if(!(!(this.I_p2<=this._)?false:true)){this._=this.A-e;break a}if(!c(this,'')){return false}break;case 4:if(!(!(this.I_pV<=this._)?false:true)){this._=this.A-e;break a}if(!c(this,'i')){return false}break}}break;case 7:if(!(!(this.I_p2<=this._)?false:true)){return false}if(!c(this,'')){return false}g=this.A-this._;i=true;a:while(i===true){i=false;this.C=this._;a=f(this,b.a_3,3);if(a===0){this._=this.A-g;break a}this.D=this._;switch(a){case 0:this._=this.A-g;break a;case 1:q=true;c:while(q===true){q=false;F=this.A-this._;s=true;b:while(s===true){s=false;if(!(!(this.I_p2<=this._)?false:true)){break b}if(!c(this,'')){return false}break c}this._=this.A-F;if(!c(this,'abl')){return false}}break;case 2:t=true;b:while(t===true){t=false;G=this.A-this._;u=true;c:while(u===true){u=false;if(!(!(this.I_p2<=this._)?false:true)){break c}if(!c(this,'')){return false}break b}this._=this.A-G;if(!c(this,'iqU')){return false}}break;case 3:if(!(!(this.I_p2<=this._)?false:true)){this._=this.A-g;break a}if(!c(this,'')){return false}break}}break;case 8:if(!(!(this.I_p2<=this._)?false:true)){return false}if(!c(this,'')){return false}h=this.A-this._;v=true;a:while(v===true){v=false;this.C=this._;if(!d(this,2,'at')){this._=this.A-h;break a}this.D=L=this._;if(!(!(this.I_p2<=L)?false:true)){this._=this.A-h;break a}if(!c(this,'')){return false}this.C=this._;if(!d(this,2,'ic')){this._=this.A-h;break a}this.D=this._;w=true;b:while(w===true){w=false;I=this.A-this._;x=true;c:while(x===true){x=false;if(!(!(this.I_p2<=this._)?false:true)){break c}if(!c(this,'')){return false}break b}this._=this.A-I;if(!c(this,'iqU')){return false}}}break;case 9:if(!c(this,'eau')){return false}break;case 10:if(!(!(this.I_p1<=this._)?false:true)){return false}if(!c(this,'al')){return false}break;case 11:y=true;a:while(y===true){y=false;A=this.A-this._;z=true;b:while(z===true){z=false;if(!(!(this.I_p2<=this._)?false:true)){break b}if(!c(this,'')){return false}break a}C=this._=this.A-A;if(!(!(this.I_p1<=C)?false:true)){return false}if(!c(this,'eux')){return false}}break;case 12:if(!(!(this.I_p1<=this._)?false:true)){return false}if(!j(this,b.g_v,97,251)){return false}if(!c(this,'')){return false}break;case 13:if(!(!(this.I_pV<=this._)?false:true)){return false}if(!c(this,'ant')){return false}return false;case 14:if(!(!(this.I_pV<=this._)?false:true)){return false}if(!c(this,'ent')){return false}return false;case 15:B=this.A-this._;if(!r(this,b.g_v,97,251)){return false}if(!(!(this.I_pV<=this._)?false:true)){return false}this._=this.A-B;if(!c(this,'')){return false}return false}return true};b.prototype.r_standard_suffix=b.prototype.Y;function K(a){var g;var F;var I;var e;var E;var h;var G;var H;var i;var J;var B;var C;var p;var l;var m;var n;var o;var k;var q;var s;var t;var u;var v;var w;var x;var y;var z;var A;var K;var L;var M;var D;a.C=a._;g=f(a,b.a_4,43);if(g===0){return false}a.D=a._;switch(g){case 0:return false;case 1:if(!(!(a.I_p2<=a._)?false:true)){return false}if(!c(a,'')){return false}break;case 2:if(!(!(a.I_p2<=a._)?false:true)){return false}if(!c(a,'')){return false}F=a.A-a._;p=true;c:while(p===true){p=false;a.C=a._;if(!d(a,2,'ic')){a._=a.A-F;break c}a.D=a._;l=true;b:while(l===true){l=false;I=a.A-a._;m=true;a:while(m===true){m=false;if(!(!(a.I_p2<=a._)?false:true)){break a}if(!c(a,'')){return false}break b}a._=a.A-I;if(!c(a,'iqU')){return false}}}break;case 3:if(!(!(a.I_p2<=a._)?false:true)){return false}if(!c(a,'log')){return false}break;case 4:if(!(!(a.I_p2<=a._)?false:true)){return false}if(!c(a,'u')){return false}break;case 5:if(!(!(a.I_p2<=a._)?false:true)){return false}if(!c(a,'ent')){return false}break;case 6:if(!(!(a.I_pV<=a._)?false:true)){return false}if(!c(a,'')){return false}e=a.A-a._;n=true;a:while(n===true){n=false;a.C=a._;g=f(a,b.a_2,6);if(g===0){a._=a.A-e;break a}a.D=a._;switch(g){case 0:a._=a.A-e;break a;case 1:if(!(!(a.I_p2<=a._)?false:true)){a._=a.A-e;break a}if(!c(a,'')){return false}a.C=a._;if(!d(a,2,'at')){a._=a.A-e;break a}a.D=K=a._;if(!(!(a.I_p2<=K)?false:true)){a._=a.A-e;break a}if(!c(a,'')){return false}break;case 2:o=true;b:while(o===true){o=false;E=a.A-a._;k=true;c:while(k===true){k=false;if(!(!(a.I_p2<=a._)?false:true)){break c}if(!c(a,'')){return false}break b}L=a._=a.A-E;if(!(!(a.I_p1<=L)?false:true)){a._=a.A-e;break a}if(!c(a,'eux')){return false}}break;case 3:if(!(!(a.I_p2<=a._)?false:true)){a._=a.A-e;break a}if(!c(a,'')){return false}break;case 4:if(!(!(a.I_pV<=a._)?false:true)){a._=a.A-e;break a}if(!c(a,'i')){return false}break}}break;case 7:if(!(!(a.I_p2<=a._)?false:true)){return false}if(!c(a,'')){return false}h=a.A-a._;q=true;a:while(q===true){q=false;a.C=a._;g=f(a,b.a_3,3);if(g===0){a._=a.A-h;break a}a.D=a._;switch(g){case 0:a._=a.A-h;break a;case 1:s=true;c:while(s===true){s=false;G=a.A-a._;t=true;b:while(t===true){t=false;if(!(!(a.I_p2<=a._)?false:true)){break b}if(!c(a,'')){return false}break c}a._=a.A-G;if(!c(a,'abl')){return false}}break;case 2:u=true;b:while(u===true){u=false;H=a.A-a._;v=true;c:while(v===true){v=false;if(!(!(a.I_p2<=a._)?false:true)){break c}if(!c(a,'')){return false}break b}a._=a.A-H;if(!c(a,'iqU')){return false}}break;case 3:if(!(!(a.I_p2<=a._)?false:true)){a._=a.A-h;break a}if(!c(a,'')){return false}break}}break;case 8:if(!(!(a.I_p2<=a._)?false:true)){return false}if(!c(a,'')){return false}i=a.A-a._;w=true;a:while(w===true){w=false;a.C=a._;if(!d(a,2,'at')){a._=a.A-i;break a}a.D=M=a._;if(!(!(a.I_p2<=M)?false:true)){a._=a.A-i;break a}if(!c(a,'')){return false}a.C=a._;if(!d(a,2,'ic')){a._=a.A-i;break a}a.D=a._;x=true;b:while(x===true){x=false;J=a.A-a._;y=true;c:while(y===true){y=false;if(!(!(a.I_p2<=a._)?false:true)){break c}if(!c(a,'')){return false}break b}a._=a.A-J;if(!c(a,'iqU')){return false}}}break;case 9:if(!c(a,'eau')){return false}break;case 10:if(!(!(a.I_p1<=a._)?false:true)){return false}if(!c(a,'al')){return false}break;case 11:z=true;a:while(z===true){z=false;B=a.A-a._;A=true;b:while(A===true){A=false;if(!(!(a.I_p2<=a._)?false:true)){break b}if(!c(a,'')){return false}break a}D=a._=a.A-B;if(!(!(a.I_p1<=D)?false:true)){return false}if(!c(a,'eux')){return false}}break;case 12:if(!(!(a.I_p1<=a._)?false:true)){return false}if(!j(a,b.g_v,97,251)){return false}if(!c(a,'')){return false}break;case 13:if(!(!(a.I_pV<=a._)?false:true)){return false}if(!c(a,'ant')){return false}return false;case 14:if(!(!(a.I_pV<=a._)?false:true)){return false}if(!c(a,'ent')){return false}return false;case 15:C=a.A-a._;if(!r(a,b.g_v,97,251)){return false}if(!(!(a.I_pV<=a._)?false:true)){return false}a._=a.A-C;if(!c(a,'')){return false}return false}return true};b.prototype.T=function(){var d;var e;var a;var g;var h;var i;e=this.A-(g=this._);if(g<this.I_pV){return false}h=this._=this.I_pV;a=this.B;this.B=h;i=this._=this.A-e;this.C=i;d=f(this,b.a_5,35);if(d===0){this.B=a;return false}this.D=this._;switch(d){case 0:this.B=a;return false;case 1:if(!j(this,b.g_v,97,251)){this.B=a;return false}if(!c(this,'')){return false}break}this.B=a;return true};b.prototype.r_i_verb_suffix=b.prototype.T;function L(a){var e;var g;var d;var h;var i;var k;g=a.A-(h=a._);if(h<a.I_pV){return false}i=a._=a.I_pV;d=a.B;a.B=i;k=a._=a.A-g;a.C=k;e=f(a,b.a_5,35);if(e===0){a.B=d;return false}a.D=a._;switch(e){case 0:a.B=d;return false;case 1:if(!j(a,b.g_v,97,251)){a.B=d;return false}if(!c(a,'')){return false}break}a.B=d;return true};b.prototype.b=function(){var e;var h;var a;var i;var g;var j;var k;var l;h=this.A-(j=this._);if(j<this.I_pV){return false}k=this._=this.I_pV;a=this.B;this.B=k;l=this._=this.A-h;this.C=l;e=f(this,b.a_6,38);if(e===0){this.B=a;return false}this.D=this._;switch(e){case 0:this.B=a;return false;case 1:if(!(!(this.I_p2<=this._)?false:true)){this.B=a;return false}if(!c(this,'')){return false}break;case 2:if(!c(this,'')){return false}break;case 3:if(!c(this,'')){return false}i=this.A-this._;g=true;a:while(g===true){g=false;this.C=this._;if(!d(this,1,'e')){this._=this.A-i;break a}this.D=this._;if(!c(this,'')){return false}}break}this.B=a;return true};b.prototype.r_verb_suffix=b.prototype.b;function M(a){var g;var i;var e;var j;var h;var k;var l;var m;i=a.A-(k=a._);if(k<a.I_pV){return false}l=a._=a.I_pV;e=a.B;a.B=l;m=a._=a.A-i;a.C=m;g=f(a,b.a_6,38);if(g===0){a.B=e;return false}a.D=a._;switch(g){case 0:a.B=e;return false;case 1:if(!(!(a.I_p2<=a._)?false:true)){a.B=e;return false}if(!c(a,'')){return false}break;case 2:if(!c(a,'')){return false}break;case 3:if(!c(a,'')){return false}j=a.A-a._;h=true;a:while(h===true){h=false;a.C=a._;if(!d(a,1,'e')){a._=a.A-j;break a}a.D=a._;if(!c(a,'')){return false}}break}a.B=e;return true};b.prototype.X=function(){var h;var g;var m;var n;var a;var l;var e;var i;var k;var p;var q;var r;var o;g=this.A-this._;e=true;a:while(e===true){e=false;this.C=this._;if(!d(this,1,'s')){this._=this.A-g;break a}this.D=p=this._;m=this.A-p;if(!j(this,b.g_keep_with_s,97,232)){this._=this.A-g;break a}this._=this.A-m;if(!c(this,'')){return false}}n=this.A-(q=this._);if(q<this.I_pV){return false}r=this._=this.I_pV;a=this.B;this.B=r;o=this._=this.A-n;this.C=o;h=f(this,b.a_7,7);if(h===0){this.B=a;return false}this.D=this._;switch(h){case 0:this.B=a;return false;case 1:if(!(!(this.I_p2<=this._)?false:true)){this.B=a;return false}i=true;a:while(i===true){i=false;l=this.A-this._;k=true;b:while(k===true){k=false;if(!d(this,1,'s')){break b}break a}this._=this.A-l;if(!d(this,1,'t')){this.B=a;return false}}if(!c(this,'')){return false}break;case 2:if(!c(this,'i')){return false}break;case 3:if(!c(this,'')){return false}break;case 4:if(!d(this,2,'gu')){this.B=a;return false}if(!c(this,'')){return false}break}this.B=a;return true};b.prototype.r_residual_suffix=b.prototype.X;function w(a){var g;var h;var p;var n;var e;var m;var i;var k;var l;var q;var r;var s;var o;h=a.A-a._;i=true;a:while(i===true){i=false;a.C=a._;if(!d(a,1,'s')){a._=a.A-h;break a}a.D=q=a._;p=a.A-q;if(!j(a,b.g_keep_with_s,97,232)){a._=a.A-h;break a}a._=a.A-p;if(!c(a,'')){return false}}n=a.A-(r=a._);if(r<a.I_pV){return false}s=a._=a.I_pV;e=a.B;a.B=s;o=a._=a.A-n;a.C=o;g=f(a,b.a_7,7);if(g===0){a.B=e;return false}a.D=a._;switch(g){case 0:a.B=e;return false;case 1:if(!(!(a.I_p2<=a._)?false:true)){a.B=e;return false}k=true;a:while(k===true){k=false;m=a.A-a._;l=true;b:while(l===true){l=false;if(!d(a,1,'s')){break b}break a}a._=a.A-m;if(!d(a,1,'t')){a.B=e;return false}}if(!c(a,'')){return false}break;case 2:if(!c(a,'i')){return false}break;case 3:if(!c(a,'')){return false}break;case 4:if(!d(a,2,'gu')){a.B=e;return false}if(!c(a,'')){return false}break}a.B=e;return true};b.prototype.a=function(){var d;var a;d=this.A-this._;if(f(this,b.a_8,5)===0){return false}a=this._=this.A-d;this.C=a;if(a<=this.B){return false}this._--;this.D=this._;return!c(this,'')?false:true};b.prototype.r_un_double=b.prototype.a;function t(a){var e;var d;e=a.A-a._;if(f(a,b.a_8,5)===0){return false}d=a._=a.A-e;a.C=d;if(d<=a.B){return false}a._--;a.D=a._;return!c(a,'')?false:true};b.prototype.Z=function(){var h;var a;var e;var f;var g;a=1;a:while(true){e=true;b:while(e===true){e=false;if(!j(this,b.g_v,97,251)){break b}a--;continue a}break a}if(a>0){return false}this.C=this._;f=true;a:while(f===true){f=false;h=this.A-this._;g=true;b:while(g===true){g=false;if(!d(this,1,'é')){break b}break a}this._=this.A-h;if(!d(this,1,'è')){return false}}this.D=this._;return!c(this,'e')?false:true};b.prototype.r_un_accent=b.prototype.Z;function F(a){var i;var e;var f;var g;var h;e=1;a:while(true){f=true;b:while(f===true){f=false;if(!j(a,b.g_v,97,251)){break b}e--;continue a}break a}if(e>0){return false}a.C=a._;g=true;a:while(g===true){g=false;i=a.A-a._;h=true;b:while(h===true){h=false;if(!d(a,1,'é')){break b}break a}a._=a.A-i;if(!d(a,1,'è')){return false}}a.D=a._;return!c(a,'e')?false:true};b.prototype.J=function(){var u;var z;var A;var B;var C;var j;var s;var v;var x;var y;var e;var f;var g;var h;var i;var a;var b;var k;var l;var m;var n;var o;var p;var q;var D;var E;var G;var N;var O;var P;var Q;var R;var r;u=this._;e=true;a:while(e===true){e=false;if(!H(this)){break a}}D=this._=u;z=D;f=true;a:while(f===true){f=false;if(!I(this)){break a}}N=this._=z;this.B=N;P=this._=O=this.A;A=O-P;g=true;c:while(g===true){g=false;h=true;d:while(h===true){h=false;B=this.A-this._;i=true;e:while(i===true){i=false;C=this.A-this._;a=true;a:while(a===true){a=false;j=this.A-this._;b=true;b:while(b===true){b=false;if(!K(this)){break b}break a}this._=this.A-j;k=true;b:while(k===true){k=false;if(!L(this)){break b}break a}this._=this.A-j;if(!M(this)){break e}}G=this._=(E=this.A)-C;s=E-G;l=true;a:while(l===true){l=false;this.C=this._;m=true;b:while(m===true){m=false;v=this.A-this._;n=true;f:while(n===true){n=false;if(!d(this,1,'Y')){break f}this.D=this._;if(!c(this,'i')){return false}break b}this._=this.A-v;if(!d(this,1,'ç')){this._=this.A-s;break a}this.D=this._;if(!c(this,'c')){return false}}}break d}this._=this.A-B;if(!w(this)){break c}}}R=this._=(Q=this.A)-A;x=Q-R;o=true;a:while(o===true){o=false;if(!t(this)){break a}}this._=this.A-x;p=true;a:while(p===true){p=false;if(!F(this)){break a}}r=this._=this.B;y=r;q=true;a:while(q===true){q=false;if(!J(this)){break a}}this._=y;return true};b.prototype.stem=b.prototype.J;b.prototype.N=function(a){return a instanceof b};b.prototype.equals=b.prototype.N;b.prototype.O=function(){var c;var a;var b;var d;c='FrenchStemmer';a=0;for(b=0;b<c.length;b++){d=c.charCodeAt(b);a=(a<<5)-a+d;a=a&a}return a|0};b.prototype.hashCode=b.prototype.O;b.serialVersionUID=1;g(b,'methodObject',function(){return new b});g(b,'a_0',function(){return[new a('col',-1,-1),new a('par',-1,-1),new a('tap',-1,-1)]});g(b,'a_1',function(){return[new a('',-1,4),new a('I',0,1),new a('U',0,2),new a('Y',0,3)]});g(b,'a_2',function(){return[new a('iqU',-1,3),new a('abl',-1,3),new a('Ièr',-1,4),new a('ièr',-1,4),new a('eus',-1,2),new a('iv',-1,1)]});g(b,'a_3',function(){return[new a('ic',-1,2),new a('abil',-1,1),new a('iv',-1,3)]});g(b,'a_4',function(){return[new a('iqUe',-1,1),new a('atrice',-1,2),new a('ance',-1,1),new a('ence',-1,5),new a('logie',-1,3),new a('able',-1,1),new a('isme',-1,1),new a('euse',-1,11),new a('iste',-1,1),new a('ive',-1,8),new a('if',-1,8),new a('usion',-1,4),new a('ation',-1,2),new a('ution',-1,4),new a('ateur',-1,2),new a('iqUes',-1,1),new a('atrices',-1,2),new a('ances',-1,1),new a('ences',-1,5),new a('logies',-1,3),new a('ables',-1,1),new a('ismes',-1,1),new a('euses',-1,11),new a('istes',-1,1),new a('ives',-1,8),new a('ifs',-1,8),new a('usions',-1,4),new a('ations',-1,2),new a('utions',-1,4),new a('ateurs',-1,2),new a('ments',-1,15),new a('ements',30,6),new a('issements',31,12),new a('ités',-1,7),new a('ment',-1,15),new a('ement',34,6),new a('issement',35,12),new a('amment',34,13),new a('emment',34,14),new a('aux',-1,10),new a('eaux',39,9),new a('eux',-1,1),new a('ité',-1,7)]});g(b,'a_5',function(){return[new a('ira',-1,1),new a('ie',-1,1),new a('isse',-1,1),new a('issante',-1,1),new a('i',-1,1),new a('irai',4,1),new a('ir',-1,1),new a('iras',-1,1),new a('ies',-1,1),new a('îmes',-1,1),new a('isses',-1,1),new a('issantes',-1,1),new a('îtes',-1,1),new a('is',-1,1),new a('irais',13,1),new a('issais',13,1),new a('irions',-1,1),new a('issions',-1,1),new a('irons',-1,1),new a('issons',-1,1),new a('issants',-1,1),new a('it',-1,1),new a('irait',21,1),new a('issait',21,1),new a('issant',-1,1),new a('iraIent',-1,1),new a('issaIent',-1,1),new a('irent',-1,1),new a('issent',-1,1),new a('iront',-1,1),new a('ît',-1,1),new a('iriez',-1,1),new a('issiez',-1,1),new a('irez',-1,1),new a('issez',-1,1)]});g(b,'a_6',function(){return[new a('a',-1,3),new a('era',0,2),new a('asse',-1,3),new a('ante',-1,3),new a('ée',-1,2),new a('ai',-1,3),new a('erai',5,2),new a('er',-1,2),new a('as',-1,3),new a('eras',8,2),new a('âmes',-1,3),new a('asses',-1,3),new a('antes',-1,3),new a('âtes',-1,3),new a('ées',-1,2),new a('ais',-1,3),new a('erais',15,2),new a('ions',-1,1),new a('erions',17,2),new a('assions',17,3),new a('erons',-1,2),new a('ants',-1,3),new a('és',-1,2),new a('ait',-1,3),new a('erait',23,2),new a('ant',-1,3),new a('aIent',-1,3),new a('eraIent',26,2),new a('èrent',-1,2),new a('assent',-1,3),new a('eront',-1,2),new a('ât',-1,3),new a('ez',-1,2),new a('iez',32,2),new a('eriez',33,2),new a('assiez',33,3),new a('erez',32,2),new a('é',-1,2)]});g(b,'a_7',function(){return[new a('e',-1,3),new a('Ière',0,2),new a('ière',0,2),new a('ion',-1,1),new a('Ier',-1,2),new a('ier',-1,2),new a('ë',-1,4)]});g(b,'a_8',function(){return[new a('ell',-1,-1),new a('eill',-1,-1),new a('enn',-1,-1),new a('onn',-1,-1),new a('ett',-1,-1)]});g(b,'g_v',function(){return[17,65,16,1,0,0,0,0,0,0,0,0,0,0,0,128,130,103,8,5]});g(b,'g_keep_with_s',function(){return[1,65,20,0,0,0,0,0,0,0,0,0,0,0,0,0,128]});var q={'src/stemmer.jsx':{Stemmer:p},'src/french-stemmer.jsx':{FrenchStemmer:b}}}(JSX))
var Stemmer = JSX.require("src/french-stemmer.jsx").FrenchStemmer;



/**
 * Simple result scoring code.
 */
var Scorer = {
  // Implement the following function to further tweak the score for each result
  // The function takes a result array [filename, title, anchor, descr, score]
  // and returns the new score.
  /*
  score: function(result) {
    return result[4];
  },
  */

  // query matches the full name of an object
  objNameMatch: 11,
  // or matches in the last dotted part of the object name
  objPartialMatch: 6,
  // Additive scores depending on the priority of the object
  objPrio: {0:  15,   // used to be importantResults
            1:  5,   // used to be objectResults
            2: -5},  // used to be unimportantResults
  //  Used when the priority is not in the mapping.
  objPrioDefault: 0,

  // query found in title
  title: 15,
  // query found in terms
  term: 5
};





var splitChars = (function() {
    var result = {};
    var singles = [96, 180, 187, 191, 215, 247, 749, 885, 903, 907, 909, 930, 1014, 1648,
         1748, 1809, 2416, 2473, 2481, 2526, 2601, 2609, 2612, 2615, 2653, 2702,
         2706, 2729, 2737, 2740, 2857, 2865, 2868, 2910, 2928, 2948, 2961, 2971,
         2973, 3085, 3089, 3113, 3124, 3213, 3217, 3241, 3252, 3295, 3341, 3345,
         3369, 3506, 3516, 3633, 3715, 3721, 3736, 3744, 3748, 3750, 3756, 3761,
         3781, 3912, 4239, 4347, 4681, 4695, 4697, 4745, 4785, 4799, 4801, 4823,
         4881, 5760, 5901, 5997, 6313, 7405, 8024, 8026, 8028, 8030, 8117, 8125,
         8133, 8181, 8468, 8485, 8487, 8489, 8494, 8527, 11311, 11359, 11687, 11695,
         11703, 11711, 11719, 11727, 11735, 12448, 12539, 43010, 43014, 43019, 43587,
         43696, 43713, 64286, 64297, 64311, 64317, 64319, 64322, 64325, 65141];
    var i, j, start, end;
    for (i = 0; i < singles.length; i++) {
        result[singles[i]] = true;
    }
    var ranges = [[0, 47], [58, 64], [91, 94], [123, 169], [171, 177], [182, 184], [706, 709],
         [722, 735], [741, 747], [751, 879], [888, 889], [894, 901], [1154, 1161],
         [1318, 1328], [1367, 1368], [1370, 1376], [1416, 1487], [1515, 1519], [1523, 1568],
         [1611, 1631], [1642, 1645], [1750, 1764], [1767, 1773], [1789, 1790], [1792, 1807],
         [1840, 1868], [1958, 1968], [1970, 1983], [2027, 2035], [2038, 2041], [2043, 2047],
         [2070, 2073], [2075, 2083], [2085, 2087], [2089, 2307], [2362, 2364], [2366, 2383],
         [2385, 2391], [2402, 2405], [2419, 2424], [2432, 2436], [2445, 2446], [2449, 2450],
         [2483, 2485], [2490, 2492], [2494, 2509], [2511, 2523], [2530, 2533], [2546, 2547],
         [2554, 2564], [2571, 2574], [2577, 2578], [2618, 2648], [2655, 2661], [2672, 2673],
         [2677, 2692], [2746, 2748], [2750, 2767], [2769, 2783], [2786, 2789], [2800, 2820],
         [2829, 2830], [2833, 2834], [2874, 2876], [2878, 2907], [2914, 2917], [2930, 2946],
         [2955, 2957], [2966, 2968], [2976, 2978], [2981, 2983], [2987, 2989], [3002, 3023],
         [3025, 3045], [3059, 3076], [3130, 3132], [3134, 3159], [3162, 3167], [3170, 3173],
         [3184, 3191], [3199, 3204], [3258, 3260], [3262, 3293], [3298, 3301], [3312, 3332],
         [3386, 3388], [3390, 3423], [3426, 3429], [3446, 3449], [3456, 3460], [3479, 3481],
         [3518, 3519], [3527, 3584], [3636, 3647], [3655, 3663], [3674, 3712], [3717, 3718],
         [3723, 3724], [3726, 3731], [3752, 3753], [3764, 3772], [3774, 3775], [3783, 3791],
         [3802, 3803], [3806, 3839], [3841, 3871], [3892, 3903], [3949, 3975], [3980, 4095],
         [4139, 4158], [4170, 4175], [4182, 4185], [4190, 4192], [4194, 4196], [4199, 4205],
         [4209, 4212], [4226, 4237], [4250, 4255], [4294, 4303], [4349, 4351], [4686, 4687],
         [4702, 4703], [4750, 4751], [4790, 4791], [4806, 4807], [4886, 4887], [4955, 4968],
         [4989, 4991], [5008, 5023], [5109, 5120], [5741, 5742], [5787, 5791], [5867, 5869],
         [5873, 5887], [5906, 5919], [5938, 5951], [5970, 5983], [6001, 6015], [6068, 6102],
         [6104, 6107], [6109, 6111], [6122, 6127], [6138, 6159], [6170, 6175], [6264, 6271],
         [6315, 6319], [6390, 6399], [6429, 6469], [6510, 6511], [6517, 6527], [6572, 6592],
         [6600, 6607], [6619, 6655], [6679, 6687], [6741, 6783], [6794, 6799], [6810, 6822],
         [6824, 6916], [6964, 6980], [6988, 6991], [7002, 7042], [7073, 7085], [7098, 7167],
         [7204, 7231], [7242, 7244], [7294, 7400], [7410, 7423], [7616, 7679], [7958, 7959],
         [7966, 7967], [8006, 8007], [8014, 8015], [8062, 8063], [8127, 8129], [8141, 8143],
         [8148, 8149], [8156, 8159], [8173, 8177], [8189, 8303], [8306, 8307], [8314, 8318],
         [8330, 8335], [8341, 8449], [8451, 8454], [8456, 8457], [8470, 8472], [8478, 8483],
         [8506, 8507], [8512, 8516], [8522, 8525], [8586, 9311], [9372, 9449], [9472, 10101],
         [10132, 11263], [11493, 11498], [11503, 11516], [11518, 11519], [11558, 11567],
         [11622, 11630], [11632, 11647], [11671, 11679], [11743, 11822], [11824, 12292],
         [12296, 12320], [12330, 12336], [12342, 12343], [12349, 12352], [12439, 12444],
         [12544, 12548], [12590, 12592], [12687, 12689], [12694, 12703], [12728, 12783],
         [12800, 12831], [12842, 12880], [12896, 12927], [12938, 12976], [12992, 13311],
         [19894, 19967], [40908, 40959], [42125, 42191], [42238, 42239], [42509, 42511],
         [42540, 42559], [42592, 42593], [42607, 42622], [42648, 42655], [42736, 42774],
         [42784, 42785], [42889, 42890], [42893, 43002], [43043, 43055], [43062, 43071],
         [43124, 43137], [43188, 43215], [43226, 43249], [43256, 43258], [43260, 43263],
         [43302, 43311], [43335, 43359], [43389, 43395], [43443, 43470], [43482, 43519],
         [43561, 43583], [43596, 43599], [43610, 43615], [43639, 43641], [43643, 43647],
         [43698, 43700], [43703, 43704], [43710, 43711], [43715, 43738], [43742, 43967],
         [44003, 44015], [44026, 44031], [55204, 55215], [55239, 55242], [55292, 55295],
         [57344, 63743], [64046, 64047], [64110, 64111], [64218, 64255], [64263, 64274],
         [64280, 64284], [64434, 64466], [64830, 64847], [64912, 64913], [64968, 65007],
         [65020, 65135], [65277, 65295], [65306, 65312], [65339, 65344], [65371, 65381],
         [65471, 65473], [65480, 65481], [65488, 65489], [65496, 65497]];
    for (i = 0; i < ranges.length; i++) {
        start = ranges[i][0];
        end = ranges[i][1];
        for (j = start; j <= end; j++) {
            result[j] = true;
        }
    }
    return result;
})();

function splitQuery(query) {
    var result = [];
    var start = -1;
    for (var i = 0; i < query.length; i++) {
        if (splitChars[query.charCodeAt(i)]) {
            if (start !== -1) {
                result.push(query.slice(start, i));
                start = -1;
            }
        } else if (start === -1) {
            start = i;
        }
    }
    if (start !== -1) {
        result.push(query.slice(start));
    }
    return result;
}




/**
 * Search Module
 */
var Search = {

  _index : null,
  _queued_query : null,
  _pulse_status : -1,

  init : function() {
      var params = $.getQueryParameters();
      if (params.q) {
          var query = params.q[0];
          $('input[name="q"]')[0].value = query;
          this.performSearch(query);
      }
  },

  loadIndex : function(url) {
    $.ajax({type: "GET", url: url, data: null,
            dataType: "script", cache: true,
            complete: function(jqxhr, textstatus) {
              if (textstatus != "success") {
                document.getElementById("searchindexloader").src = url;
              }
            }});
  },

  setIndex : function(index) {
    var q;
    this._index = index;
    if ((q = this._queued_query) !== null) {
      this._queued_query = null;
      Search.query(q);
    }
  },

  hasIndex : function() {
      return this._index !== null;
  },

  deferQuery : function(query) {
      this._queued_query = query;
  },

  stopPulse : function() {
      this._pulse_status = 0;
  },

  startPulse : function() {
    if (this._pulse_status >= 0)
        return;
    function pulse() {
      var i;
      Search._pulse_status = (Search._pulse_status + 1) % 4;
      var dotString = '';
      for (i = 0; i < Search._pulse_status; i++)
        dotString += '.';
      Search.dots.text(dotString);
      if (Search._pulse_status > -1)
        window.setTimeout(pulse, 500);
    }
    pulse();
  },

  /**
   * perform a search for something (or wait until index is loaded)
   */
  performSearch : function(query) {
    // create the required interface elements
    this.out = $('#search-results');
    this.title = $('<h2>' + _('Searching') + '</h2>').appendTo(this.out);
    this.dots = $('<span></span>').appendTo(this.title);
    this.status = $('<p style="display: none"></p>').appendTo(this.out);
    this.output = $('<ul class="search"/>').appendTo(this.out);

    $('#search-progress').text(_('Preparing search...'));
    this.startPulse();

    // index already loaded, the browser was quick!
    if (this.hasIndex())
      this.query(query);
    else
      this.deferQuery(query);
  },

  /**
   * execute search (requires search index to be loaded)
   */
  query : function(query) {
    var i;
    var stopwords = ["ai","aie","aient","aies","ait","as","au","aura","aurai","auraient","aurais","aurait","auras","aurez","auriez","aurions","aurons","auront","aux","avaient","avais","avait","avec","avez","aviez","avions","avons","ayant","ayez","ayons","c","ce","ceci","cela","cel\u00e0","ces","cet","cette","d","dans","de","des","du","elle","en","es","est","et","eu","eue","eues","eurent","eus","eusse","eussent","eusses","eussiez","eussions","eut","eux","e\u00fbmes","e\u00fbt","e\u00fbtes","furent","fus","fusse","fussent","fusses","fussiez","fussions","fut","f\u00fbmes","f\u00fbt","f\u00fbtes","ici","il","ils","j","je","l","la","le","les","leur","leurs","lui","m","ma","mais","me","mes","moi","mon","m\u00eame","n","ne","nos","notre","nous","on","ont","ou","par","pas","pour","qu","que","quel","quelle","quelles","quels","qui","s","sa","sans","se","sera","serai","seraient","serais","serait","seras","serez","seriez","serions","serons","seront","ses","soi","soient","sois","soit","sommes","son","sont","soyez","soyons","suis","sur","t","ta","te","tes","toi","ton","tu","un","une","vos","votre","vous","y","\u00e0","\u00e9taient","\u00e9tais","\u00e9tait","\u00e9tant","\u00e9tiez","\u00e9tions","\u00e9t\u00e9","\u00e9t\u00e9e","\u00e9t\u00e9es","\u00e9t\u00e9s","\u00eates"];

    // stem the searchterms and add them to the correct list
    var stemmer = new Stemmer();
    var searchterms = [];
    var excluded = [];
    var hlterms = [];
    var tmp = splitQuery(query);
    var objectterms = [];
    for (i = 0; i < tmp.length; i++) {
      if (tmp[i] !== "") {
          objectterms.push(tmp[i].toLowerCase());
      }

      if ($u.indexOf(stopwords, tmp[i].toLowerCase()) != -1 || tmp[i].match(/^\d+$/) ||
          tmp[i] === "") {
        // skip this "word"
        continue;
      }
      // stem the word
      var word = stemmer.stemWord(tmp[i].toLowerCase());
      // prevent stemmer from cutting word smaller than two chars
      if(word.length < 3 && tmp[i].length >= 3) {
        word = tmp[i];
      }
      var toAppend;
      // select the correct list
      if (word[0] == '-') {
        toAppend = excluded;
        word = word.substr(1);
      }
      else {
        toAppend = searchterms;
        hlterms.push(tmp[i].toLowerCase());
      }
      // only add if not already in the list
      if (!$u.contains(toAppend, word))
        toAppend.push(word);
    }
    var highlightstring = '?highlight=' + $.urlencode(hlterms.join(" "));

    // console.debug('SEARCH: searching for:');
    // console.info('required: ', searchterms);
    // console.info('excluded: ', excluded);

    // prepare search
    var terms = this._index.terms;
    var titleterms = this._index.titleterms;

    // array of [filename, title, anchor, descr, score]
    var results = [];
    $('#search-progress').empty();

    // lookup as object
    for (i = 0; i < objectterms.length; i++) {
      var others = [].concat(objectterms.slice(0, i),
                             objectterms.slice(i+1, objectterms.length));
      results = results.concat(this.performObjectSearch(objectterms[i], others));
    }

    // lookup as search terms in fulltext
    results = results.concat(this.performTermsSearch(searchterms, excluded, terms, titleterms));

    // let the scorer override scores with a custom scoring function
    if (Scorer.score) {
      for (i = 0; i < results.length; i++)
        results[i][4] = Scorer.score(results[i]);
    }

    // now sort the results by score (in opposite order of appearance, since the
    // display function below uses pop() to retrieve items) and then
    // alphabetically
    results.sort(function(a, b) {
      var left = a[4];
      var right = b[4];
      if (left > right) {
        return 1;
      } else if (left < right) {
        return -1;
      } else {
        // same score: sort alphabetically
        left = a[1].toLowerCase();
        right = b[1].toLowerCase();
        return (left > right) ? -1 : ((left < right) ? 1 : 0);
      }
    });

    // for debugging
    //Search.lastresults = results.slice();  // a copy
    //console.info('search results:', Search.lastresults);

    // print the results
    var resultCount = results.length;
    function displayNextItem() {
      // results left, load the summary and display it
      if (results.length) {
        var item = results.pop();
        var listItem = $('<li style="display:none"></li>');
        if (DOCUMENTATION_OPTIONS.FILE_SUFFIX === '') {
          // dirhtml builder
          var dirname = item[0] + '/';
          if (dirname.match(/\/index\/$/)) {
            dirname = dirname.substring(0, dirname.length-6);
          } else if (dirname == 'index/') {
            dirname = '';
          }
          listItem.append($('<a/>').attr('href',
            DOCUMENTATION_OPTIONS.URL_ROOT + dirname +
            highlightstring + item[2]).html(item[1]));
        } else {
          // normal html builders
          listItem.append($('<a/>').attr('href',
            item[0] + DOCUMENTATION_OPTIONS.FILE_SUFFIX +
            highlightstring + item[2]).html(item[1]));
        }
        if (item[3]) {
          listItem.append($('<span> (' + item[3] + ')</span>'));
          Search.output.append(listItem);
          listItem.slideDown(5, function() {
            displayNextItem();
          });
        } else if (DOCUMENTATION_OPTIONS.HAS_SOURCE) {
          var suffix = DOCUMENTATION_OPTIONS.SOURCELINK_SUFFIX;
          if (suffix === undefined) {
            suffix = '.txt';
          }
          $.ajax({url: DOCUMENTATION_OPTIONS.URL_ROOT + '_sources/' + item[5] + (item[5].slice(-suffix.length) === suffix ? '' : suffix),
                  dataType: "text",
                  complete: function(jqxhr, textstatus) {
                    var data = jqxhr.responseText;
                    if (data !== '' && data !== undefined) {
                      listItem.append(Search.makeSearchSummary(data, searchterms, hlterms));
                    }
                    Search.output.append(listItem);
                    listItem.slideDown(5, function() {
                      displayNextItem();
                    });
                  }});
        } else {
          // no source available, just display title
          Search.output.append(listItem);
          listItem.slideDown(5, function() {
            displayNextItem();
          });
        }
      }
      // search finished, update title and status message
      else {
        Search.stopPulse();
        Search.title.text(_('Search Results'));
        if (!resultCount)
          Search.status.text(_('Your search did not match any documents. Please make sure that all words are spelled correctly and that you\'ve selected enough categories.'));
        else
            Search.status.text(_('Search finished, found %s page(s) matching the search query.').replace('%s', resultCount));
        Search.status.fadeIn(500);
      }
    }
    displayNextItem();
  },

  /**
   * search for object names
   */
  performObjectSearch : function(object, otherterms) {
    var filenames = this._index.filenames;
    var docnames = this._index.docnames;
    var objects = this._index.objects;
    var objnames = this._index.objnames;
    var titles = this._index.titles;

    var i;
    var results = [];

    for (var prefix in objects) {
      for (var name in objects[prefix]) {
        var fullname = (prefix ? prefix + '.' : '') + name;
        if (fullname.toLowerCase().indexOf(object) > -1) {
          var score = 0;
          var parts = fullname.split('.');
          // check for different match types: exact matches of full name or
          // "last name" (i.e. last dotted part)
          if (fullname == object || parts[parts.length - 1] == object) {
            score += Scorer.objNameMatch;
          // matches in last name
          } else if (parts[parts.length - 1].indexOf(object) > -1) {
            score += Scorer.objPartialMatch;
          }
          var match = objects[prefix][name];
          var objname = objnames[match[1]][2];
          var title = titles[match[0]];
          // If more than one term searched for, we require other words to be
          // found in the name/title/description
          if (otherterms.length > 0) {
            var haystack = (prefix + ' ' + name + ' ' +
                            objname + ' ' + title).toLowerCase();
            var allfound = true;
            for (i = 0; i < otherterms.length; i++) {
              if (haystack.indexOf(otherterms[i]) == -1) {
                allfound = false;
                break;
              }
            }
            if (!allfound) {
              continue;
            }
          }
          var descr = objname + _(', in ') + title;

          var anchor = match[3];
          if (anchor === '')
            anchor = fullname;
          else if (anchor == '-')
            anchor = objnames[match[1]][1] + '-' + fullname;
          // add custom score for some objects according to scorer
          if (Scorer.objPrio.hasOwnProperty(match[2])) {
            score += Scorer.objPrio[match[2]];
          } else {
            score += Scorer.objPrioDefault;
          }
          results.push([docnames[match[0]], fullname, '#'+anchor, descr, score, filenames[match[0]]]);
        }
      }
    }

    return results;
  },

  /**
   * search for full-text terms in the index
   */
  performTermsSearch : function(searchterms, excluded, terms, titleterms) {
    var docnames = this._index.docnames;
    var filenames = this._index.filenames;
    var titles = this._index.titles;

    var i, j, file;
    var fileMap = {};
    var scoreMap = {};
    var results = [];

    // perform the search on the required terms
    for (i = 0; i < searchterms.length; i++) {
      var word = searchterms[i];
      var files = [];
      var _o = [
        {files: terms[word], score: Scorer.term},
        {files: titleterms[word], score: Scorer.title}
      ];

      // no match but word was a required one
      if ($u.every(_o, function(o){return o.files === undefined;})) {
        break;
      }
      // found search word in contents
      $u.each(_o, function(o) {
        var _files = o.files;
        if (_files === undefined)
          return

        if (_files.length === undefined)
          _files = [_files];
        files = files.concat(_files);

        // set score for the word in each file to Scorer.term
        for (j = 0; j < _files.length; j++) {
          file = _files[j];
          if (!(file in scoreMap))
            scoreMap[file] = {}
          scoreMap[file][word] = o.score;
        }
      });

      // create the mapping
      for (j = 0; j < files.length; j++) {
        file = files[j];
        if (file in fileMap)
          fileMap[file].push(word);
        else
          fileMap[file] = [word];
      }
    }

    // now check if the files don't contain excluded terms
    for (file in fileMap) {
      var valid = true;

      // check if all requirements are matched
      if (fileMap[file].length != searchterms.length)
          continue;

      // ensure that none of the excluded terms is in the search result
      for (i = 0; i < excluded.length; i++) {
        if (terms[excluded[i]] == file ||
            titleterms[excluded[i]] == file ||
            $u.contains(terms[excluded[i]] || [], file) ||
            $u.contains(titleterms[excluded[i]] || [], file)) {
          valid = false;
          break;
        }
      }

      // if we have still a valid result we can add it to the result list
      if (valid) {
        // select one (max) score for the file.
        // for better ranking, we should calculate ranking by using words statistics like basic tf-idf...
        var score = $u.max($u.map(fileMap[file], function(w){return scoreMap[file][w]}));
        results.push([docnames[file], titles[file], '', null, score, filenames[file]]);
      }
    }
    return results;
  },

  /**
   * helper function to return a node containing the
   * search summary for a given text. keywords is a list
   * of stemmed words, hlwords is the list of normal, unstemmed
   * words. the first one is used to find the occurrence, the
   * latter for highlighting it.
   */
  makeSearchSummary : function(text, keywords, hlwords) {
    var textLower = text.toLowerCase();
    var start = 0;
    $.each(keywords, function() {
      var i = textLower.indexOf(this.toLowerCase());
      if (i > -1)
        start = i;
    });
    start = Math.max(start - 120, 0);
    var excerpt = ((start > 0) ? '...' : '') +
      $.trim(text.substr(start, 240)) +
      ((start + 240 - text.length) ? '...' : '');
    var rv = $('<div class="context"></div>').text(excerpt);
    $.each(hlwords, function() {
      rv = rv.highlightText(this, 'highlighted');
    });
    return rv;
  }
};

$(document).ready(function() {
  Search.init();
});