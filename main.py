from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sympy import sympify, integrate, latex, symbols, lambdify
import numpy as np

app = FastAPI(title="MathPro 12 Backend")

# Cho phép Frontend truy cập (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

x_sym = symbols('x')

# --- CỔNG PING ĐỂ GIỮ SERVER 24/7 ---
@app.get("/ping")
async def ping():
    """Cổng này giúp Cron-job đánh thức server mà không tốn RAM"""
    return {"status": "awake", "message": "I am ready to solve math!"}

@app.get("/solve")
async def solve(expr: str, lower: str = None, upper: str = None):
    try:
        # Làm sạch chuỗi nhập vào
        clean_expr = expr.replace('^', '**')
        f = sympify(clean_expr)
        
        if lower and upper:
            a, b = sympify(lower), sympify(upper)
            res = integrate(f, (x_sym, a, b))
            # Thể tích tròn xoay Ox: V = pi * integral(f^2)
            v_res = integrate(f**2, (x_sym, a, b))
            
            return {
                "status": "success",
                "result_latex": latex(res),
                "volume_latex": latex(v_res),
                "display": f"\\int_{{{latex(a)}}}^{{{latex(b)}}} {latex(f)} dx = {latex(res)}"
            }
        else:
            res = integrate(f, x_sym)
            return {
                "status": "success",
                "display": f"\\int {latex(f)} dx = {latex(res)} + C"
            }
    except Exception as e:
        return {"status": "error", "message": "Biểu thức quá khó hoặc sai định dạng!"}

@app.get("/plot-data")
async def plot_data(expr: str, lower: float, upper: float):
    try:
        f_sym = sympify(expr.replace('^', '**'))
        f_num = lambdify(x_sym, f_sym, "numpy")
        x_vals = np.linspace(lower, upper, 60) 
        y_vals = f_num(x_vals)
        return {"status": "success", "x": x_vals.tolist(), "y": y_vals.tolist()}
    except:
        return {"status": "error"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
