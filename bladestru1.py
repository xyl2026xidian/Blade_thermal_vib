# turbine_animation_step.py - 涡轮叶片工作原理（逐帧动画）
import streamlit as st
import plotly.graph_objects as go
import numpy as np

# ========== 页面配置 ==========
st.set_page_config(
    page_title="涡轮叶片工作原理",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 涡轮叶片工作原理 - 逐帧动画")
st.markdown("**点击按钮，叶片旋转一个角度，观察结构变化**")
st.markdown("---")


# ============================================================
# 创建单帧涡轮叶片
# ============================================================

def create_turbine_frame(frame=0, num_blades=8, show_gas=True, show_forces=True):
    """创建单帧涡轮叶片3D图"""

    fig = go.Figure()

    hub_radius = 1.2
    blade_length = 2.0
    blade_width = 0.35
    blade_thickness = 0.08
    angle_offset = frame * 0.08  # 每步旋转角度

    # ===== 轮盘 =====
    theta = np.linspace(0, 2 * np.pi, 50)
    phi = np.linspace(0, 2 * np.pi, 30)
    Theta, Phi = np.meshgrid(theta, phi)
    R_hub = hub_radius * np.ones_like(Theta)
    X_hub = R_hub * np.cos(Theta)
    Y_hub = R_hub * np.sin(Theta)
    Z_hub = 0.4 * np.sin(Phi)

    fig.add_trace(go.Surface(
        x=X_hub, y=Y_hub, z=Z_hub,
        colorscale=[[0, '#2c3e50'], [1, '#34495e']],
        opacity=0.9, showscale=False, name='轮盘'
    ))

    # ===== 转轴 =====
    axis_z = np.linspace(-2.5, 2.5, 20)
    fig.add_trace(go.Scatter3d(
        x=[0] * len(axis_z), y=[0] * len(axis_z), z=axis_z,
        mode='lines', line=dict(color='#7f8c8d', width=8), name='转轴'
    ))

    # ===== 叶片 =====
    blade_colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71',
                    '#1abc9c', '#3498db', '#9b59b6', '#e91e63']

    for i in range(num_blades):
        angle = i * 2 * np.pi / num_blades + angle_offset
        base_x = (hub_radius + 0.1) * np.cos(angle)
        base_y = (hub_radius + 0.1) * np.sin(angle)
        radial_dir = np.array([np.cos(angle), np.sin(angle), 0])
        tangent_dir = np.array([-np.sin(angle), np.cos(angle), 0])

        n_points = 20
        r_vals = np.linspace(0, blade_length, n_points)
        width_profile = blade_width * (1 - 0.5 * r_vals / blade_length)
        twist = 0.5 * r_vals / blade_length

        x_leaf, y_leaf, z_leaf = [], [], []
        for j, r in enumerate(r_vals):
            pos = base_x + r * radial_dir[0]
            pos_y = base_y + r * radial_dir[1]
            pos_z = 0.1 * r / blade_length
            w = width_profile[j]
            t = twist[j]
            corners = [(-w / 2, -blade_thickness / 2), (w / 2, -blade_thickness / 2),
                       (w / 2, blade_thickness / 2), (-w / 2, blade_thickness / 2)]
            for c in corners:
                local_x = c[0] * np.cos(t) - c[1] * np.sin(t)
                local_y = c[0] * np.sin(t) + c[1] * np.cos(t)
                x_leaf.append(pos + local_x * tangent_dir[0] + local_y * radial_dir[0])
                y_leaf.append(pos_y + local_x * tangent_dir[1] + local_y * radial_dir[1])
                z_leaf.append(pos_z)

        n_sections = n_points
        n_corners = 4
        i_idx, j_idx, k_idx = [], [], []
        for s in range(n_sections - 1):
            for c in range(n_corners):
                v0 = s * n_corners + c
                v1 = s * n_corners + (c + 1) % n_corners
                v2 = (s + 1) * n_corners + c
                v3 = (s + 1) * n_corners + (c + 1) % n_corners
                i_idx.extend([v0, v0, v1])
                j_idx.extend([v1, v2, v2])
                k_idx.extend([v2, v3, v3])

        fig.add_trace(go.Mesh3d(
            x=x_leaf, y=y_leaf, z=z_leaf,
            i=i_idx, j=j_idx, k=k_idx,
            color=blade_colors[i % len(blade_colors)],
            opacity=0.85, showscale=False,
            name=f'叶片 {i + 1}',
            hoverinfo='text',
            hovertext=f'叶片 {i + 1}<br>受燃气冲击旋转'
        ))

    # ===== 燃气流动 =====
    if show_gas:
        for i in range(12):
            arrow_angle = i * 2 * np.pi / 12 + angle_offset * 0.5
            start_r = 4.0 + 0.3 * np.sin(angle_offset * 2 + i)
            start_x = start_r * np.cos(arrow_angle)
            start_y = start_r * np.sin(arrow_angle)
            start_z = 0.1 * np.sin(angle_offset + i)
            end_r = 2.8 + 0.2 * np.sin(angle_offset * 1.5 + i * 0.5)
            end_x = end_r * np.cos(arrow_angle - 0.15)
            end_y = end_r * np.sin(arrow_angle - 0.15)
            end_z = 0.1 * np.sin(angle_offset * 0.8 + i * 0.3)
            color_val = 0.5 + 0.5 * (i / 12)
            arrow_color = f'rgb({int(255 * color_val)}, {int(100 * color_val)}, 0)'
            fig.add_trace(go.Scatter3d(
                x=[start_x, end_x], y=[start_y, end_y], z=[start_z, end_z],
                mode='lines', line=dict(color=arrow_color, width=3),
                showlegend=False, hoverinfo='skip'
            ))

    # ===== 受力箭头 =====
    if show_forces:
        for i in range(num_blades):
            angle = i * 2 * np.pi / num_blades + angle_offset
            force_r = hub_radius + blade_length * 0.5
            force_x = force_r * np.cos(angle)
            force_y = force_r * np.sin(angle)
            force_z = 0.1
            tang_x = -np.sin(angle)
            tang_y = np.cos(angle)
            arrow_len = 0.5
            fig.add_trace(go.Scatter3d(
                x=[force_x, force_x + arrow_len * tang_x],
                y=[force_y, force_y + arrow_len * tang_y],
                z=[force_z, force_z],
                mode='lines', line=dict(color='#00ff00', width=4),
                showlegend=False, hoverinfo='skip'
            ))
            fig.add_trace(go.Scatter3d(
                x=[force_x + arrow_len * tang_x],
                y=[force_y + arrow_len * tang_y],
                z=[force_z],
                mode='markers',
                marker=dict(size=8, color='#00ff00', symbol='circle'),
                showlegend=False, hoverinfo='skip'
            ))

    # ===== 标注 =====
    fig.add_trace(go.Scatter3d(
        x=[4.5], y=[0], z=[0.5],
        mode='text', text=['🔥 高温燃气'],
        textfont=dict(size=14, color='red'), showlegend=False, hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter3d(
        x=[-3.5], y=[0], z=[1.0],
        mode='text', text=['↻ 旋转方向'],
        textfont=dict(size=14, color='#f39c12'), showlegend=False, hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[2.5],
        mode='text', text=['⬆ 功率输出'],
        textfont=dict(size=14, color='#2ecc71'), showlegend=False, hoverinfo='skip'
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='', showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(title='', showgrid=False, showticklabels=False, zeroline=False),
            zaxis=dict(title='', showgrid=False, showticklabels=False, zeroline=False),
            aspectmode='manual', aspectratio=dict(x=1.5, y=1.5, z=1.0),
            camera=dict(eye=dict(x=1.8, y=1.8, z=1.2), center=dict(x=0, y=0, z=0)),
            bgcolor='rgba(0,0,0,0)'
        ),
        height=700, margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig


# ============================================================
# 控制面板
# ============================================================
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    num_blades = st.slider("叶片数量", 4, 12, 8)
    step_angle = st.slider("每步旋转角度", 1, 20, 10)

with col2:
    show_gas = st.checkbox("🔥 显示燃气流动", value=True)
    show_forces = st.checkbox("💪 显示受力箭头", value=True)

with col3:
    st.write("")
    st.write("")
    reset_btn = st.button("⟲ 重置视角", use_container_width=True)

st.markdown("---")

# ============================================================
# 核心交互：按钮驱动
# ============================================================

# 初始化帧数
if 'frame' not in st.session_state:
    st.session_state.frame = 0

# 控制按钮
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn1:
    if st.button("◀ 逆时针旋转", use_container_width=True):
        st.session_state.frame -= 1

with col_btn2:
    if st.button("⟳ 重置位置", use_container_width=True):
        st.session_state.frame = 0

with col_btn3:
    if st.button("顺时针旋转 ▶", use_container_width=True):
        st.session_state.frame += 1

# 显示当前帧信息
st.info(f"📍 当前帧: {st.session_state.frame}  |  旋转角度: {st.session_state.frame * step_angle:.0f}°")

st.markdown("---")

# ============================================================
# 渲染当前帧
# ============================================================

fig = create_turbine_frame(
    frame=st.session_state.frame,
    num_blades=num_blades,
    show_gas=show_gas,
    show_forces=show_forces
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 工作原理说明
# ============================================================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.info("**🔥 第1步：燃气冲击**\n\n高温高压燃气冲击叶片表面")
with col2:
    st.success("**⚡ 第2步：产生力矩**\n\n切向力驱动叶片旋转")
with col3:
    st.warning("**💪 第3步：做功输出**\n\n通过转轴输出机械功")

st.markdown("---")
st.caption("🚀 点击按钮逐帧观察 | 交互式教学工具")