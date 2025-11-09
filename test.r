# Tạo dãy giá trị cho x
x <- seq(-10, 10, by = 0.1)

# Tính giá trị y = 3x
ysudo <- 3 * x

# Vẽ đồ thị
c = plot(x, y, type = "l", col = "blue", lwd = 2,
     main = "Đồ thị y = 3x",
     xlab = "x",
     ylab = "y = 3x",
     grid = TRUE)
