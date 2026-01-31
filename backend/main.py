from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sympy import sympify, integrate, latex, symbols, lambdify
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

x_sym = symbols('x')

@app.get("/solve")
async def solve(expr: str, lower: str = None, upper: str = None):
    try:
        # Chuyển đổi công thức sang định dạng Sympy
        f = sympify(expr.replace('^', '**'))
        
        if lower and upper:
            a, b = sympify(lower), sympify(upper)
            res = integrate(f, (x_sym, a, b))
            # Tính thể tích vật thể tròn xoay quanh Ox: V = pi * integral(f^2)
            v_res = integrate(np.pi * (f**2), (x_sym, a, b))
            
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
                "result_latex": f"{latex(res)} + C",
                "display": f"\\int {latex(f)} dx = {latex(res)} + C"
            }
    except Exception as e:
        return {"status": "error", "message": "Biểu thức quá phức tạp hoặc sai định dạng!"}

@app.get("/plot-data")
async def plot_data(expr: str, lower: float, upper: float):
    try:
        f_sym = sympify(expr.replace('^', '**'))
        f_num = lambdify(x_sym, f_sym, "numpy")
        
        x_vals = np.linspace(lower, upper, 50) # 50 điểm để tiết kiệm băng thông
        y_vals = f_num(x_vals)
        
        return {
            "status": "success",
            "x": x_vals.tolist(),
            "y": y_vals.tolist()
        }
    except:
        return {"status": "error"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
