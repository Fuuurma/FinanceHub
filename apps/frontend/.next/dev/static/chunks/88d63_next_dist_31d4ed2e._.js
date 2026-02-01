(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/apps/frontend/src/node_modules/next/dist/server/app-render/async-local-storage.js [app-client] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
0 && (module.exports = {
    bindSnapshot: null,
    createAsyncLocalStorage: null,
    createSnapshot: null
});
function _export(target, all) {
    for(var name in all)Object.defineProperty(target, name, {
        enumerable: true,
        get: all[name]
    });
}
_export(exports, {
    bindSnapshot: function() {
        return bindSnapshot;
    },
    createAsyncLocalStorage: function() {
        return createAsyncLocalStorage;
    },
    createSnapshot: function() {
        return createSnapshot;
    }
});
const sharedAsyncLocalStorageNotAvailableError = Object.defineProperty(new Error('Invariant: AsyncLocalStorage accessed in runtime where it is not available'), "__NEXT_ERROR_CODE", {
    value: "E504",
    enumerable: false,
    configurable: true
});
class FakeAsyncLocalStorage {
    disable() {
        throw sharedAsyncLocalStorageNotAvailableError;
    }
    getStore() {
        // This fake implementation of AsyncLocalStorage always returns `undefined`.
        return undefined;
    }
    run() {
        throw sharedAsyncLocalStorageNotAvailableError;
    }
    exit() {
        throw sharedAsyncLocalStorageNotAvailableError;
    }
    enterWith() {
        throw sharedAsyncLocalStorageNotAvailableError;
    }
    static bind(fn) {
        return fn;
    }
}
const maybeGlobalAsyncLocalStorage = typeof globalThis !== 'undefined' && globalThis.AsyncLocalStorage;
function createAsyncLocalStorage() {
    if (maybeGlobalAsyncLocalStorage) {
        return new maybeGlobalAsyncLocalStorage();
    }
    return new FakeAsyncLocalStorage();
}
function bindSnapshot(fn) {
    if (maybeGlobalAsyncLocalStorage) {
        return maybeGlobalAsyncLocalStorage.bind(fn);
    }
    return FakeAsyncLocalStorage.bind(fn);
}
function createSnapshot() {
    if (maybeGlobalAsyncLocalStorage) {
        return maybeGlobalAsyncLocalStorage.snapshot();
    }
    return function(fn, ...args) {
        return fn(...args);
    };
} //# sourceMappingURL=async-local-storage.js.map
}),
"[project]/apps/frontend/src/node_modules/next/dist/server/app-render/work-async-storage-instance.js [app-client] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
Object.defineProperty(exports, "workAsyncStorageInstance", {
    enumerable: true,
    get: function() {
        return workAsyncStorageInstance;
    }
});
const _asynclocalstorage = __turbopack_context__.r("[project]/apps/frontend/src/node_modules/next/dist/server/app-render/async-local-storage.js [app-client] (ecmascript)");
const workAsyncStorageInstance = (0, _asynclocalstorage.createAsyncLocalStorage)(); //# sourceMappingURL=work-async-storage-instance.js.map
}),
"[project]/apps/frontend/src/node_modules/next/dist/server/app-render/work-async-storage.external.js [app-client] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
Object.defineProperty(exports, "workAsyncStorage", {
    enumerable: true,
    get: function() {
        return _workasyncstorageinstance.workAsyncStorageInstance;
    }
});
const _workasyncstorageinstance = __turbopack_context__.r("[project]/apps/frontend/src/node_modules/next/dist/server/app-render/work-async-storage-instance.js [app-client] (ecmascript)"); //# sourceMappingURL=work-async-storage.external.js.map
}),
"[project]/apps/frontend/src/node_modules/next/dist/client/components/handle-isr-error.js [app-client] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
Object.defineProperty(exports, "HandleISRError", {
    enumerable: true,
    get: function() {
        return HandleISRError;
    }
});
const workAsyncStorage = typeof window === 'undefined' ? __turbopack_context__.r("[project]/apps/frontend/src/node_modules/next/dist/server/app-render/work-async-storage.external.js [app-client] (ecmascript)").workAsyncStorage : undefined;
function HandleISRError({ error }) {
    if (workAsyncStorage) {
        const store = workAsyncStorage.getStore();
        if (store?.isStaticGeneration) {
            if (error) {
                console.error(error);
            }
            throw error;
        }
    }
    return null;
}
if ((typeof exports.default === 'function' || typeof exports.default === 'object' && exports.default !== null) && typeof exports.default.__esModule === 'undefined') {
    Object.defineProperty(exports.default, '__esModule', {
        value: true
    });
    Object.assign(exports.default, exports);
    module.exports = exports.default;
} //# sourceMappingURL=handle-isr-error.js.map
}),
"[project]/apps/frontend/src/node_modules/next/dist/client/components/builtin/error-styles.js [app-client] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
0 && (module.exports = {
    ErrorIcon: null,
    errorStyles: null,
    errorThemeCss: null
});
function _export(target, all) {
    for(var name in all)Object.defineProperty(target, name, {
        enumerable: true,
        get: all[name]
    });
}
_export(exports, {
    ErrorIcon: function() {
        return ErrorIcon;
    },
    errorStyles: function() {
        return errorStyles;
    },
    errorThemeCss: function() {
        return errorThemeCss;
    }
});
const _interop_require_default = __turbopack_context__.r("[project]/apps/frontend/node_modules/@swc/helpers/cjs/_interop_require_default.cjs [app-client] (ecmascript)");
const _jsxruntime = __turbopack_context__.r("[project]/apps/frontend/node_modules/next/dist/compiled/react/jsx-runtime.js [app-client] (ecmascript)");
const _react = /*#__PURE__*/ _interop_require_default._(__turbopack_context__.r("[project]/apps/frontend/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)"));
const errorStyles = {
    container: {
        fontFamily: 'system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji"',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
    },
    card: {
        maxWidth: '420px',
        padding: '32px 28px',
        textAlign: 'left'
    },
    icon: {
        marginBottom: '16px'
    },
    title: {
        fontSize: '17px',
        fontWeight: 600,
        letterSpacing: '-0.01em',
        margin: '0 0 8px 0',
        color: 'var(--next-error-title)'
    },
    message: {
        fontSize: '14px',
        fontWeight: 400,
        lineHeight: 1.6,
        margin: '0 0 6px 0',
        color: 'var(--next-error-message)'
    },
    messageHint: {
        fontSize: '13px',
        fontWeight: 400,
        lineHeight: 1.5,
        margin: '0 0 20px 0',
        color: 'var(--next-error-hint)'
    },
    buttonGroup: {
        display: 'flex',
        gap: '12px',
        alignItems: 'center'
    },
    button: {
        padding: '10px 20px',
        fontSize: '14px',
        fontWeight: 500,
        letterSpacing: '0.01em',
        borderRadius: '6px',
        cursor: 'pointer',
        color: 'var(--next-error-btn-text)',
        background: 'var(--next-error-btn-bg)',
        border: 'var(--next-error-btn-border)'
    },
    buttonSecondary: {
        padding: '10px 20px',
        fontSize: '14px',
        fontWeight: 500,
        letterSpacing: '0.01em',
        borderRadius: '6px',
        cursor: 'pointer',
        color: 'var(--next-error-btn-secondary-text)',
        background: 'transparent',
        border: 'none'
    },
    digestContainer: {
        marginTop: '20px',
        paddingTop: '16px',
        borderTop: 'var(--next-error-digest-border)'
    },
    digest: {
        fontSize: '12px',
        fontWeight: 400,
        margin: '0',
        color: 'var(--next-error-digest)'
    },
    digestCode: {
        fontFamily: 'ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace',
        fontSize: '11px',
        color: 'var(--next-error-digest-code)',
        userSelect: 'all'
    }
};
const errorThemeCss = `
:root {
  --next-error-bg: #fff;
  --next-error-text: #171717;
  --next-error-title: #171717;
  --next-error-message: #666;
  --next-error-hint: #888;
  --next-error-digest: #999;
  --next-error-digest-code: #888;
  --next-error-digest-border: 1px solid rgba(0,0,0,0.06);
  --next-error-btn-text: #171717;
  --next-error-btn-bg: #fff;
  --next-error-btn-border: 1px solid #e5e5e5;
  --next-error-btn-secondary-text: #666;
  --next-error-icon-ring: #fecaca;
  --next-error-icon-fill: #fef2f2;
}
@media (prefers-color-scheme: dark) {
  :root {
    --next-error-bg: #0a0a0a;
    --next-error-text: #ededed;
    --next-error-title: #ededed;
    --next-error-message: #a0a0a0;
    --next-error-hint: #707070;
    --next-error-digest: #606060;
    --next-error-digest-code: #707070;
    --next-error-digest-border: 1px solid rgba(255,255,255,0.08);
    --next-error-btn-text: #ededed;
    --next-error-btn-bg: #1a1a1a;
    --next-error-btn-border: 1px solid #333;
    --next-error-btn-secondary-text: #a0a0a0;
    --next-error-icon-ring: #5c2121;
    --next-error-icon-fill: #2a1618;
  }
}
body { margin: 0; color: var(--next-error-text); background: var(--next-error-bg); }
`.replace(/\n\s*/g, '');
function ErrorIcon() {
    return /*#__PURE__*/ (0, _jsxruntime.jsxs)("svg", {
        width: "40",
        height: "40",
        viewBox: "0 0 40 40",
        fill: "none",
        style: errorStyles.icon,
        children: [
            /*#__PURE__*/ (0, _jsxruntime.jsx)("circle", {
                cx: "20",
                cy: "20",
                r: "19",
                stroke: "var(--next-error-icon-ring)",
                strokeWidth: "2"
            }),
            /*#__PURE__*/ (0, _jsxruntime.jsx)("circle", {
                cx: "20",
                cy: "20",
                r: "16",
                fill: "var(--next-error-icon-fill)"
            }),
            /*#__PURE__*/ (0, _jsxruntime.jsx)("path", {
                d: "M20 12v9",
                stroke: "#dc2626",
                strokeWidth: "2.5",
                strokeLinecap: "round"
            }),
            /*#__PURE__*/ (0, _jsxruntime.jsx)("circle", {
                cx: "20",
                cy: "27",
                r: "1.5",
                fill: "#dc2626"
            })
        ]
    });
}
if ((typeof exports.default === 'function' || typeof exports.default === 'object' && exports.default !== null) && typeof exports.default.__esModule === 'undefined') {
    Object.defineProperty(exports.default, '__esModule', {
        value: true
    });
    Object.assign(exports.default, exports);
    module.exports = exports.default;
} //# sourceMappingURL=error-styles.js.map
}),
"[project]/apps/frontend/src/node_modules/next/dist/client/components/builtin/global-error.js [app-client] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
Object.defineProperty(exports, // supplied custom global error signatures.
"default", {
    enumerable: true,
    get: function() {
        return _default;
    }
});
const _jsxruntime = __turbopack_context__.r("[project]/apps/frontend/node_modules/next/dist/compiled/react/jsx-runtime.js [app-client] (ecmascript)");
const _handleisrerror = __turbopack_context__.r("[project]/apps/frontend/src/node_modules/next/dist/client/components/handle-isr-error.js [app-client] (ecmascript)");
const _errorstyles = __turbopack_context__.r("[project]/apps/frontend/src/node_modules/next/dist/client/components/builtin/error-styles.js [app-client] (ecmascript)");
function DefaultGlobalError({ error }) {
    const digest = error?.digest;
    const isServerError = !!digest;
    // Server error: "This page failed to load"
    // Client error: "This page crashed"
    const title = isServerError ? 'This page failed to load' : 'This page crashed';
    const message = isServerError ? 'Something went wrong while loading this page.' : 'An error occurred while running this page.';
    const hint = isServerError ? 'If this keeps happening, it may be a server issue.' : null;
    return /*#__PURE__*/ (0, _jsxruntime.jsxs)("html", {
        id: "__next_error__",
        children: [
            /*#__PURE__*/ (0, _jsxruntime.jsx)("head", {
                children: /*#__PURE__*/ (0, _jsxruntime.jsx)("style", {
                    dangerouslySetInnerHTML: {
                        __html: _errorstyles.errorThemeCss
                    }
                })
            }),
            /*#__PURE__*/ (0, _jsxruntime.jsxs)("body", {
                children: [
                    /*#__PURE__*/ (0, _jsxruntime.jsx)(_handleisrerror.HandleISRError, {
                        error: error
                    }),
                    /*#__PURE__*/ (0, _jsxruntime.jsx)("div", {
                        style: _errorstyles.errorStyles.container,
                        children: /*#__PURE__*/ (0, _jsxruntime.jsxs)("div", {
                            style: _errorstyles.errorStyles.card,
                            children: [
                                /*#__PURE__*/ (0, _jsxruntime.jsx)(_errorstyles.ErrorIcon, {}),
                                /*#__PURE__*/ (0, _jsxruntime.jsx)("h1", {
                                    style: _errorstyles.errorStyles.title,
                                    children: title
                                }),
                                /*#__PURE__*/ (0, _jsxruntime.jsx)("p", {
                                    style: _errorstyles.errorStyles.message,
                                    children: message
                                }),
                                hint && /*#__PURE__*/ (0, _jsxruntime.jsx)("p", {
                                    style: _errorstyles.errorStyles.messageHint,
                                    children: hint
                                }),
                                !isServerError && /*#__PURE__*/ (0, _jsxruntime.jsx)("p", {
                                    style: _errorstyles.errorStyles.messageHint,
                                    children: "Reloading usually fixes this."
                                }),
                                /*#__PURE__*/ (0, _jsxruntime.jsxs)("div", {
                                    style: _errorstyles.errorStyles.buttonGroup,
                                    children: [
                                        /*#__PURE__*/ (0, _jsxruntime.jsx)("form", {
                                            children: /*#__PURE__*/ (0, _jsxruntime.jsx)("button", {
                                                type: "submit",
                                                style: _errorstyles.errorStyles.button,
                                                children: "Reload page"
                                            })
                                        }),
                                        !isServerError && /*#__PURE__*/ (0, _jsxruntime.jsx)("button", {
                                            type: "button",
                                            style: _errorstyles.errorStyles.buttonSecondary,
                                            onClick: ()=>{
                                                if (window.history.length > 1) {
                                                    window.history.back();
                                                } else {
                                                    window.location.href = '/';
                                                }
                                            },
                                            children: "Go back"
                                        })
                                    ]
                                }),
                                digest && /*#__PURE__*/ (0, _jsxruntime.jsx)("div", {
                                    style: _errorstyles.errorStyles.digestContainer,
                                    children: /*#__PURE__*/ (0, _jsxruntime.jsxs)("p", {
                                        style: _errorstyles.errorStyles.digest,
                                        children: [
                                            "Error reference:",
                                            ' ',
                                            /*#__PURE__*/ (0, _jsxruntime.jsx)("code", {
                                                style: _errorstyles.errorStyles.digestCode,
                                                children: digest
                                            })
                                        ]
                                    })
                                })
                            ]
                        })
                    })
                ]
            })
        ]
    });
}
const _default = DefaultGlobalError;
if ((typeof exports.default === 'function' || typeof exports.default === 'object' && exports.default !== null) && typeof exports.default.__esModule === 'undefined') {
    Object.defineProperty(exports.default, '__esModule', {
        value: true
    });
    Object.assign(exports.default, exports);
    module.exports = exports.default;
} //# sourceMappingURL=global-error.js.map
}),
]);

//# sourceMappingURL=88d63_next_dist_31d4ed2e._.js.map