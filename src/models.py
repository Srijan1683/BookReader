from dataclasses import dataclass

@dataclass
class TOC:
    """ Data Class for tuples obtained for TOC """
    level: int
    title: str
    page_number: int
    
@dataclass
class ChapterTOC:
    """ Data Class to hold TOC of each chapter"""
    number: int
    title: str
    start_page: int
    end_page: int
    chapter_toc_list: list[TOC]

@dataclass
class Page:
    number: int
    content: str
    
    
@dataclass
class Headings:
    title: str
    text: str
    page_number: int
