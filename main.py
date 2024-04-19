import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx

params_entry = None
result_label = None
ax = None
canvas = None
fuzzy_table = None
fuzzy_result_label = None
tree_table_before = None
tree_table_after = None


def trapezoidal_mf(x, a, b, c, d):
    mf = []
    for i in x:
        if i <= a:
            mf.append(0)
        elif a < i <= b:
            mf.append((i - a) / (b - a))
        elif b < i <= c:
            mf.append(1)
        elif c < i <= d:
            mf.append((d - i) / (d - c))
        else:
            mf.append(0)
    return mf

def mean_of_maximum(x, mf):
    max_val = max(mf)
    indices = [i for i, v in enumerate(mf) if v == max_val]
    return sum(x[i] for i in indices) / len(indices)

def calculate_result():
    global params_entry, ax, canvas, fuzzy_table, result_label
    params = [float(p.strip()) for p in params_entry.get().split(',')]
    a, b, c, d = params
    x = [i * (d - a) / 999 + a for i in range(1000)]
    mf = trapezoidal_mf(x, a, b, c, d)
    ax.clear()
    ax.plot(x, mf, 'b-', linewidth=2)
    ax.fill_between(x, mf, color='b', alpha=0.2)
    ax.set_xlabel("x")
    ax.set_ylabel("Степень принадлежности")
    ax.set_title("АТФП")
    ax.grid(True)
    canvas.draw()
    
    fuzzy_table.delete(*fuzzy_table.get_children())
    for i in range(len(x)):
        fuzzy_table.insert("", tk.END, values=(x[i], mf[i]))

def calculate_fuzzy_number():
    global fuzzy_table, fuzzy_result_label
    x_values = []
    mu_values = []
    for item in fuzzy_table.get_children():
        x, mu = fuzzy_table.item(item, "values")
        x_values.append(float(x))
        mu_values.append(float(mu))
    result = mean_of_maximum(x_values, mu_values)
    fuzzy_result_label.config(text=f"Четкое число: {result:.2f}")

def remove_node():
    global tree_table_after
    selected_item = tree_table_after.selection()
    if selected_item:
        tree_table_after.delete(selected_item)
        update_tree_visualization_after(ax_after, canvas_after)

def reset_default():
    global params_entry, fuzzy_table, result_label, fuzzy_result_label, ax, canvas
    params_entry.delete(0, tk.END)
    fuzzy_table.delete(*fuzzy_table.get_children())
    result_label.config(text="")
    fuzzy_result_label.config(text="")
    ax.clear()
    canvas.draw()
    generate_fuzzy_binary_tree()

def generate_fuzzy_binary_tree():
    global tree_table_before, tree_table_after
    tree_table_before.delete(*tree_table_before.get_children())
    tree_table_after.delete(*tree_table_after.get_children())
    
    def generate_subtree(parent, depth):
        if depth == 0:
            return
        
        left_child = tree_table_before.insert(parent, "end", text=f"Node {tree_table_before.index(parent) * 2 + 1}", values=())
        right_child = tree_table_before.insert(parent, "end", text=f"Node {tree_table_before.index(parent) * 2 + 2}", values=())
        
        generate_subtree(left_child, depth - 1)
        generate_subtree(right_child, depth - 1)
    
    root = tree_table_before.insert("", "end", text="Root", values=())
    generate_subtree(root, 3)
    update_tree_after()
    update_tree_visualization_after(ax_after, canvas_after)
    update_tree_visualizations(ax_before, canvas_before)

def draw_tree(tree_table, canvas):
    G = nx.DiGraph()
    
    def add_nodes(parent, node):
        node_text = tree_table.item(node, "text")
        G.add_node(node_text)
        if parent:
            parent_text = tree_table.item(parent, "text")
            G.add_edge(parent_text, node_text)
        for child in tree_table.get_children(node):
            add_nodes(node, child)
    
    for root in tree_table.get_children():
        add_nodes("", root)
    
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=500, node_color='green', font_size=12, font_weight='bold', ax=canvas)

def update_tree_visualizations(ax_before, canvas_before):
    ax_before.clear()
    draw_tree(tree_table_before, ax_before)
    canvas_before.draw()

def update_tree_visualization_after(ax_after, canvas_after):
    ax_after.clear()
    draw_tree(tree_table_after, ax_after)
    canvas_after.draw()

def update_tree_after():
    global tree_table_before, tree_table_after
    tree_table_after.delete(*tree_table_after.get_children())
    
    def copy_node(parent_item, node_item):
        node_text = tree_table_before.item(node_item, "text")
        new_item = tree_table_after.insert(parent_item, "end", text=node_text, values=())
        for child_item in tree_table_before.get_children(node_item):
            copy_node(new_item, child_item)
    
    for root_item in tree_table_before.get_children():
        copy_node("", root_item)

def open_trees_window():
    global tree_table_before, tree_table_after, tree_table_static, ax_before, ax_after, ax_static, canvas_before, canvas_after, canvas_static
    trees_window = tk.Toplevel(root)
    trees_window.title("Деревья")
    
    tree_frame = ttk.LabelFrame(trees_window, text="Статическое")
    tree_frame.pack(padx=10, pady=10)

    tree_frame_before = ttk.LabelFrame(tree_frame, text="")
    tree_frame_before.pack(side=tk.LEFT, padx=10)

    tree_table_before = ttk.Treeview(tree_frame_before)
    tree_table_before.pack()

    tree_frame_after = ttk.LabelFrame(tree_frame, text="Эксплотируемое")
    tree_frame_after.pack(side=tk.RIGHT, padx=10)

    tree_table_after = ttk.Treeview(tree_frame_after)
    tree_table_after.pack()

    button_frame = ttk.Frame(tree_frame)
    button_frame.pack(side=tk.LEFT, padx=10, pady=10)

    button_frame = ttk.Frame(tree_frame)
    button_frame.pack(side=tk.LEFT, padx=10, pady=10)

    remove_button = ttk.Button(button_frame, text="Удалить элемент", command=remove_node)
    remove_button.pack(pady=5)

    reset_button = ttk.Button(button_frame, text="Сгенерировать новое дерево", command=generate_fuzzy_binary_tree)
    reset_button.pack(pady=5)

    fig_before = Figure(figsize=(5, 4), dpi=100)
    ax_before = fig_before.add_subplot(111)
    canvas_before = FigureCanvasTkAgg(fig_before, master=tree_frame_before)
    canvas_before.get_tk_widget().pack()

    fig_after = Figure(figsize=(5, 4), dpi=100)
    ax_after = fig_after.add_subplot(111)
    canvas_after = FigureCanvasTkAgg(fig_after, master=tree_frame_after)
    canvas_after.get_tk_widget().pack()

    generate_fuzzy_binary_tree()
    update_tree_after()
    update_tree_visualizations(ax_before, canvas_before)
    update_tree_visualization_after(ax_after, canvas_after)

def open_atfp_msm_window():
    global params_entry, result_label, ax, canvas, fuzzy_table, fuzzy_result_label
    atfp_msm_window = tk.Toplevel(root)
    atfp_msm_window.title("АТФП/МСМ")
    
    atfp_frame = ttk.LabelFrame(atfp_msm_window, text="АТФП")
    atfp_frame.pack(padx=10, pady=10)

    params_label = ttk.Label(atfp_frame, text="Параметры (через запятую):")
    params_label.pack()

    params_entry = ttk.Entry(atfp_frame)
    params_entry.pack()

    calculate_button = ttk.Button(atfp_frame, text="Рассчитать", command=calculate_result)
    calculate_button.pack()

    reset_button = ttk.Button(atfp_frame, text="Сброс", command=reset_default)
    reset_button.pack()

    result_label = ttk.Label(atfp_frame, text="")
    result_label.pack()

    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=atfp_frame)
    canvas.get_tk_widget().pack()

    fuzzy_frame = ttk.LabelFrame(atfp_msm_window, text="Нечеткое число")
    fuzzy_frame.pack(padx=10, pady=10)

    fuzzy_table = ttk.Treeview(fuzzy_frame, columns=("x", "mu"), show="headings")
    fuzzy_table.heading("x", text="x")
    fuzzy_table.heading("mu", text="μ")
    fuzzy_table.pack()

    fuzzy_calculate_button = ttk.Button(fuzzy_frame, text="Рассчитать четкое число", command=calculate_fuzzy_number)
    fuzzy_calculate_button.pack()

    fuzzy_result_label = ttk.Label(fuzzy_frame, text="")
    fuzzy_result_label.pack()

root = tk.Tk()
root.title("Расчетно-графическая работа")

main_frame = ttk.Frame(root)
main_frame.pack(padx=70, pady=70)

trees_button = ttk.Button(main_frame, text="Нечеткое бинарное дерево", command=open_trees_window)
trees_button.pack(pady=5)

atfp_msm_button = ttk.Button(main_frame, text="АТФП/МСМ", command=open_atfp_msm_window)
atfp_msm_button.pack(pady=5)

root.mainloop()