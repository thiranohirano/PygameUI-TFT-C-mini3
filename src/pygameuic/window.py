import pygame
rect = None

def col_rect(col, row, col_span, row_span, margin=5):
    padding = 5
    one_col = (rect.w - margin * 2) // 12
    one_row = (rect.h - margin * 2) // 8
    return pygame.Rect(col * one_col + padding + margin, row * one_row + padding + margin, col_span * one_col - padding * 2, row_span * one_row - padding * 2)

def col_rect_mini(col, row, col_span, row_span, margin=5, padding=5):
    one_col = (rect.w - margin * 2) // 8
    one_row = (rect.h - margin * 2) // 6
    return pygame.Rect(col * one_col + padding + margin, row * one_row + padding + margin, col_span * one_col - padding * 2, row_span * one_row - padding * 2)
