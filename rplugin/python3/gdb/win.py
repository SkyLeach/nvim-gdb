class Win:
    def __init__(self, vim, win, cursor, client, breakpoint):
        self.vim = vim
        # window number that will be displaying the current file
        self.jumpWin = win
        self.cursor = cursor
        self.client = client
        self.breakpoint = breakpoint

    def jump(self, file, line):
        # Make sure all the operations happen in the correct window
        window = self.vim.current.window
        self.vim.command("%dwincmd w" % self.jumpWin.number)

        # Check whether the file is already loaded or load it
        targetBuf = self.vim.call("bufnr", file, 1)

        # The terminal buffer may contain the name of the source file (in pdb, for
        # instance)
        if targetBuf == self.client.getBuf().handle:
            self.vim.command("noswapfile view " + file)
            targetBuf = self.vim.call("bufnr", file)

        # Switch to the new buffer if necessary
        if self.vim.call("bufnr", '%') != targetBuf:
            self.vim.command('noswapfile buffer %d' % targetBuf)

        # Goto the proper line and set the cursor on it
        self.vim.command(':%d' % line)
        self.cursor.set(targetBuf, line)
        self.cursor.show()

        # Return to the original window for the user
        self.vim.command("%dwincmd w" % window.number)


    def queryBreakpoints(self):
        pass
        ## Get the source code buffer number
        #bufNum = self.jumpWin.buffer

        ## Get the source code file name
        #fname = gdb.getFullBufferPath(bufNum)

        #-- If no file name or a weird name with spaces, ignore it (to avoid
        #-- misinterpretation)
        #if fname != '' and fname\find(' ') == nil
        #    -- Query the breakpoints for the shown file
        #    @breakpoint\query(bufNum, fname)
        #    -- If there was a cursor, make sure it stays above the breakpoints.
        #    V.gdb_py {"dispatch", "cursor", "reshow"}

        #-- Execute the rest of custom commands
        #V.exe "doautocmd User NvimGdbQuery"
