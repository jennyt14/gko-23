import numpy as np

def method2(A, x, y, case, LH1, LH2, LHk, TOL):
    
    # LH is the left hand side of convergence rate: 
    ## LH1 is for first iterate
    ## LH2 is for the second iterate (used for GKO and MWRKO only)
    ## LHk is for the k-th iterate
    
    k=1
    m, n = A.shape
    x_old = np.zeros(n)
    # e0 = ||x0 - x*||^2
    ar = (np.linalg.norm(x_old-x))**2
    ap_error = [ar]
    #ap_error.append(ar)
    upper_bd = [ar]
    gk_LHS_lst = []
    gko_LHS_lst = [LH1]
    mwrko_LHS_lst = [LH1]

    
    # first iterate (k = 1)
    if case == 'GKO' or case == 'MWRKO':
        inner_p = A@np.transpose(A)
        row_lst = [] 
        resid = abs(A@x_old - y)
        denom = np.sum(np.abs(A)**2,axis=-1)**(1./2)
        i1 = np.argmax(resid/denom)
        a1 = A[i1,:]
        x1 = x_old - ((a1@x_old - y[i1]) / np.linalg.norm(a1)**2) * np.transpose(a1)
        # add upper_bd: ||x1 - x*||^2 <= LH1 * ||x0 - x*||^2
        bd = LH1 * ar
        upper_bd.append(bd)
        # update x
        x_old = x1
        row_lst.append(i1)
        ar = (np.linalg.norm(x_old-x))**2
        ap_error.append(ar)
        k += 1
        ik = row_lst[-1]
    
    while True:
        rhat = A@x_old - y
        match case:
            case "GK":
                r = (rhat)**2
                i = np.argmax(r)
                ai = A[i,:]
                xk = x_old - ((np.transpose(ai)@x_old - y[i]) /  np.linalg.norm(ai)**2 * ai)
                # compute upper_bd: ||xk - x*||^2 <= LH * ||x(k-1) - x*||^2
                gamma = np.linalg.norm(A@xk - y)**2 / np.linalg.norm(A@xk - y, np.inf)**2
                gk_LHS_lst.append(1 - (LHk / gamma))
                bd = np.prod(gk_LHS_lst) * (np.linalg.norm(np.zeros(n) - x)**2)
                upper_bd.append(bd)
            case "GKO":
                inner_dig = np.delete(inner_p.diagonal(), ik)
                all_comb = np.delete(inner_p[:,ik], ik)
                denom = inner_dig - np.square(all_comb) / np.linalg.norm(A[ik,:])**2
                resid  = np.delete(abs(rhat), ik)
                i_k1 = np.argmax(resid/np.sqrt(denom))
                if (i_k1 >= ik):
                  i_k1 += 1
                row_lst.append(i_k1)
                r = A[i_k1,:]@x_old - y[i_k1]
                w = A[i_k1,:] - ((inner_p[ik, i_k1] / np.linalg.norm( A[ik,:])**2) * A[ik,:])
                t = r / np.linalg.norm(w)**2
                xk = x_old - t*w
                # compute upper_bd: ||xk - x*||^2 <= LH * ||x(k-1) - x*||^2
                D = np.linalg.inv(np.diag(w))
                U,S,V = np.linalg.svd(D)
                DS2_min = min(S**2)
                AD = A @ D
                # compute dynamic range
                gamma = np.linalg.norm(AD@x_old - AD@x)**2 / np.linalg.norm(AD@x_old - AD@x, np.inf)**2
  
                #old_gamma = np.linalg.norm(A@x_old - y)**2 / np.linalg.norm(A@x_old - y, np.inf)**2
                if k == 2:
                    gko_LHS_lst.append(1 - (LH2 * DS2_min / gamma))
                    bd = np.prod(gko_LHS_lst) * (np.linalg.norm(np.zeros(n) - x)**2)
                    upper_bd.append(bd)
                else:
                    gko_LHS_lst.append(1 - (LHk * DS2_min / gamma))
                    bd = np.prod(gko_LHS_lst) * (np.linalg.norm(np.zeros(n) - x)**2)
                    upper_bd.append(bd)
            case "MWRKO":
                resid = abs(rhat)
                i_k1 = np.argmax(resid/denom)
                row_lst.append(i_k1)
                r = A[i_k1,:]@x_old - y[i_k1]
                w = A[i_k1,:] - ((inner_p[ik, i_k1] / np.linalg.norm( A[ik,:])**2) * A[ik,:])
                t = r / np.linalg.norm(w)**2
                xk = x_old - t*w 
                # compute upper_bd: ||xk - x*||^2 <= LH * ||x(k-1) - x*||^2
                if k == 2:
                    mwrko_LHS_lst.append(LH2)
                    bd = np.prod(mwrko_LHS_lst) * (np.linalg.norm(np.zeros(n) - x)**2)
                    upper_bd.append(bd)
                else:
                    mwrko_LHS_lst.append(LHk)
                    bd = np.prod(mwrko_LHS_lst) * (np.linalg.norm(np.zeros(n) - x)**2)
                    upper_bd.append(bd)
  
        # update x and approximation error
        x_old = xk
        ar = (np.linalg.norm(x_old-x))**2
        gamma = np.linalg.norm(A@x_old - y)**2 / np.linalg.norm(A@x_old - y, np.inf)**2
        ap_error.append(ar)
        k+=1
        
        
        if ar < TOL or k == 100000:
            #print(len(gk_LHS_lst))
            #print(len(gko_LHS_lst))
            #print(len(mwrko_LHS_lst))
            #if case == 'GK':
            # compute upper_bd: ||xk - x*||^2 <= LH * ||x(k-1) - x*||^2
            #    gk_LHS_lst.append(1 - (LHk / gamma))
            #    bd = np.prod(gk_LHS_lst) * (np.linalg.norm(np.zeros(n) - x)**2)
            #    upper_bd.append(bd)
            #if case == 'GKO':
            #    bd = ( 1 - LHk / gamma ) * ar
            #    upper_bd.append(bd)
            break
            
    return k, ap_error, upper_bd