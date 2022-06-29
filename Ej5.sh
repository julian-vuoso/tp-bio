#!/bin/bash

getorf -minsize 300 -sequence sequence.gb -outseq emboss.orf
prosextract -prositedir .
patmatmotifs -full -sequence emboss.orf -outfile emboss.patmatmotifs
